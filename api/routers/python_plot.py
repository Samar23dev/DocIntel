import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

ALLOWED_IMPORTS = {"matplotlib", "matplotlib.pyplot", "numpy", "pandas"}
BLOCKED_NAMES = {"__import__", "eval", "exec", "compile", "open", "input", "globals", "locals", "vars"}


class PlotRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000)


class PlotResponse(BaseModel):
    svg: str


def validate_code(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Python: {exc.msg}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name not in ALLOWED_IMPORTS for alias in node.names):
                raise HTTPException(status_code=400, detail="Only matplotlib, NumPy, and pandas imports are allowed")
        elif isinstance(node, ast.ImportFrom):
            if node.module not in ALLOWED_IMPORTS:
                raise HTTPException(status_code=400, detail="Only matplotlib, NumPy, and pandas imports are allowed")
        elif isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            raise HTTPException(status_code=400, detail=f"Python name '{node.id}' is not allowed")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"savefig", "save", "show"}:
            continue
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise HTTPException(status_code=400, detail="Private Python attributes are not allowed")


@router.post("/python/plot", response_model=PlotResponse)
def render_plot(request: PlotRequest) -> PlotResponse:
    validate_code(request.code)

    with tempfile.TemporaryDirectory(prefix="docintel-plot-") as directory:
        output = Path(directory) / "plot.svg"
        script = Path(directory) / "plot.py"
        script.write_text(
            "import matplotlib\nmatplotlib.use('Agg')\n" + request.code.rstrip()
            + "\n\nimport matplotlib.pyplot as _plt\n_plt.savefig(r'" + str(output) + "', format='svg', bbox_inches='tight')\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.update({"MPLBACKEND": "Agg", "MPLCONFIGDIR": directory, "HOME": directory})
        try:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=directory, env=env,
                capture_output=True, text=True, timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="Plot generation timed out")

        if result.returncode != 0 or not output.exists() or output.stat().st_size > 5_000_000:
            message = result.stderr.strip().splitlines()
            raise HTTPException(status_code=400, detail=(message[-1] if message else "Plot generation failed"))

        svg = output.read_text(encoding="utf-8")
        if "<svg" not in svg or "<script" in svg.lower():
            raise HTTPException(status_code=400, detail="Generated output is not a safe SVG")
        return PlotResponse(svg=svg)

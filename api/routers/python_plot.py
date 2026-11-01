import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

router = APIRouter()

ALLOWED_IMPORTS = {"matplotlib", "matplotlib.pyplot", "numpy", "pandas", "plotly", "plotly.express", "plotly.graph_objects", "plotly.io"}
BLOCKED_NAMES = {"__import__", "eval", "exec", "compile", "open", "input", "globals", "locals", "vars"}


class PlotRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=20000)


class PlotResponse(BaseModel):
    svg: str


class PlotlyResponse(BaseModel):
    figure: dict


def validate_code(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Python: {exc.msg}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name not in ALLOWED_IMPORTS for alias in node.names):
                raise HTTPException(status_code=400, detail="Only matplotlib, Plotly, NumPy, and pandas imports are allowed")
        elif isinstance(node, ast.ImportFrom):
            if node.module not in ALLOWED_IMPORTS:
                raise HTTPException(status_code=400, detail="Only matplotlib, Plotly, NumPy, and pandas imports are allowed")
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
            logger.error("Matplotlib plot generation timed out")
            raise HTTPException(status_code=408, detail="Plot generation timed out")

        if result.returncode != 0 or not output.exists() or output.stat().st_size > 5_000_000:
            logger.error(
                "Matplotlib plot generation failed:\nstdout={}\nstderr={}",
                result.stdout.strip(),
                result.stderr.strip(),
            )
            raise HTTPException(status_code=400, detail="The generated Matplotlib code could not be rendered.")

        svg = output.read_text(encoding="utf-8")
        if "<svg" not in svg or "<script" in svg.lower():
            logger.error("Matplotlib renderer returned unsafe or invalid SVG output")
            raise HTTPException(status_code=400, detail="Generated output is not a safe SVG")
        return PlotResponse(svg=svg)


@router.post("/python/plotly", response_model=PlotlyResponse)
def render_plotly(request: PlotRequest) -> PlotlyResponse:
    validate_code(request.code)

    with tempfile.TemporaryDirectory(prefix="docintel-plotly-") as directory:
        output = Path(directory) / "figure.json"
        script = Path(directory) / "plot.py"
        script.write_text(
            request.code.rstrip()
            + "\n\nimport plotly.io as _pio\n_pio.write_json(fig, r'"
            + str(output)
            + "')\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env.update({"HOME": directory})
        try:
            result = subprocess.run(
                [sys.executable, str(script)], cwd=directory, env=env,
                capture_output=True, text=True, timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.error("Plotly chart generation timed out")
            raise HTTPException(status_code=408, detail="Plotly generation timed out")

        if result.returncode != 0 or not output.exists() or output.stat().st_size > 5_000_000:
            logger.error(
                "Plotly chart generation failed:\nstdout={}\nstderr={}",
                result.stdout.strip(),
                result.stderr.strip(),
            )
            raise HTTPException(status_code=400, detail="The generated Plotly code could not be rendered.")

        import json
        try:
            return PlotlyResponse(figure=json.loads(output.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError) as exc:
            logger.exception("Plotly figure JSON was invalid: {}", exc)
            raise HTTPException(status_code=400, detail="The generated Plotly figure was invalid.")

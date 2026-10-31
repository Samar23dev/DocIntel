import pytest
from fastapi import HTTPException

from api.routers.python_plot import PlotRequest, render_plot, validate_code


def test_plot_endpoint_renders_matplotlib_svg():
    response = render_plot(PlotRequest(code="import matplotlib.pyplot as plt\nplt.plot([1, 2, 3], [3, 2, 1])"))
    assert "<svg" in response.svg


def test_plot_rejects_file_access_import():
    with pytest.raises(HTTPException) as exc:
        validate_code("import os")
    assert exc.value.status_code == 400


def test_plot_rejects_python_execution_calls():
    with pytest.raises(HTTPException) as exc:
        validate_code("eval('1 + 1')")
    assert exc.value.status_code == 400

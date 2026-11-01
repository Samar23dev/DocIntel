from langchain_core.messages import HumanMessage

from open_notebook.utils.mermaid import mermaid_instruction_for_messages
from open_notebook.utils.python_plot import python_plot_instruction_for_messages
from open_notebook.utils.vega_lite import vega_lite_instruction_for_messages


def test_mermaid_generation_is_disabled():
    messages = [HumanMessage(content="Create a flowchart showing login authentication")]
    assert mermaid_instruction_for_messages(messages) is None


def test_explicit_mermaid_generation_is_disabled():
    instruction = mermaid_instruction_for_messages([
        HumanMessage(content="Create a Mermaid architecture diagram")
    ])

    assert instruction is None


def test_mermaid_request_does_not_match_normal_chat():
    messages = [HumanMessage(content="Explain how authentication works")]
    assert mermaid_instruction_for_messages(messages) is None


def test_python_plot_request_is_enabled_by_default():
    messages = [HumanMessage(content="Create a line chart for quarterly revenue")]
    assert python_plot_instruction_for_messages(messages)


def test_tikz_request_is_not_sent_to_python_plot_specialist():
    messages = [HumanMessage(content=r"Convert this TikZ figure to a plot: \begin{tikzpicture}\end{tikzpicture}")]
    assert python_plot_instruction_for_messages(messages) is None


def test_explicit_vega_lite_chart_uses_vega_lite_specialist():
    messages = [HumanMessage(content="Create a Vega-Lite line chart for quarterly revenue")]
    instruction = vega_lite_instruction_for_messages(messages)

    assert instruction is not None
    assert "```vega-lite" in instruction
    assert "Vega-Lite v5" in instruction

from langchain_core.messages import HumanMessage

from open_notebook.utils.mermaid import mermaid_instruction_for_messages
from open_notebook.utils.python_plot import python_plot_instruction_for_messages


def test_mermaid_request_adds_specialist_instruction():
    messages = [HumanMessage(content="Create a flowchart showing login authentication")]
    assert mermaid_instruction_for_messages(messages)


def test_mermaid_request_does_not_match_normal_chat():
    messages = [HumanMessage(content="Explain how authentication works")]
    assert mermaid_instruction_for_messages(messages) is None


def test_python_plot_request_adds_specialist_instruction():
    messages = [HumanMessage(content="Create a line chart for quarterly revenue")]
    assert python_plot_instruction_for_messages(messages)


def test_tikz_request_adds_plot_specialist_instruction():
    messages = [HumanMessage(content=r"Convert this TikZ figure to a plot: \begin{tikzpicture}\end{tikzpicture}")]
    assert python_plot_instruction_for_messages(messages)

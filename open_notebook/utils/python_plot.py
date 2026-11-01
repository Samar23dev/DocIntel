from langchain_core.messages import HumanMessage

PYTHON_PLOT_INSTRUCTION = """# PYTHON PLOT SPECIALIST
When the user asks for a Matplotlib data chart, graph, or plot, produce one complete, executable Python block using the ```python-plot fence. Use matplotlib.pyplot, NumPy, or pandas only when needed. Do not use file access, subprocesses, network requests, imports other than matplotlib, numpy, and pandas, or savefig calls. Keep the code focused on building one chart. The application renders it automatically; do not call plt.show(). Add a short explanation before or after the block."""


def python_plot_instruction_for_messages(messages: list) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = message.content if isinstance(message.content, str) else str(message.content)
            normalized = text.lower()
            if "tikz" in normalized or "pgfplots" in normalized:
                return None
            chart_terms = ("chart", "graph", "plot", "histogram", "scatter", "bar chart", "line chart", "pie chart")
            requests_plot = any(word in normalized for word in ("create", "draw", "generate", "make", "show", "plot", "chart", "convert", "render", "use"))
            if any(term in normalized for term in chart_terms) and requests_plot:
                return PYTHON_PLOT_INSTRUCTION
            return None
    return None

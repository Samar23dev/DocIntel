from langchain_core.messages import HumanMessage

PYTHON_PLOT_INSTRUCTION = """# PYTHON PLOT SPECIALIST
When the user asks for a Matplotlib chart, graph, plot, TikZ/PGFPlots figure, or LaTeX plot code, produce one complete, executable Python block using the ```python-plot fence. Use matplotlib.pyplot, NumPy, or pandas only when needed. Do not use file access, subprocesses, network requests, imports other than matplotlib, numpy, and pandas, or savefig calls. Keep the code focused on building one chart. The application renders it automatically; do not call plt.show(). Add a short explanation before or after the block."""


def python_plot_instruction_for_messages(messages: list) -> str | None:
    # Matplotlib/Python chat generation is temporarily disabled so charts can
    # be evaluated through safer declarative Vega-Lite output first.
    return None

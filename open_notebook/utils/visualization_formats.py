DEFAULT_VISUALIZATION_INSTRUCTION = """# DEFAULT VISUALIZATION FORMATS
Do not choose Mermaid for default visualizations or diagrams.
Prefer Graphviz DOT in one fenced ```dot block for relationships, architecture, workflows, and dense diagrams.
Use executable Matplotlib Python in one fenced ```python-plot block for default data charts.
Use Plotly Python in one fenced ```plotly-plot block when interactive Plotly charts are requested or selected during regeneration.
Use Vega-Lite JSON in one fenced ```vega-lite block only when Vega-Lite is explicitly requested or selected during regeneration.
Only use Mermaid when the user explicitly asks for Mermaid or selects Mermaid during visualization regeneration."""

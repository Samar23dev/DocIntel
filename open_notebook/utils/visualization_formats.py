DEFAULT_VISUALIZATION_INSTRUCTION = """# DEFAULT VISUALIZATION FORMATS
Do not choose Mermaid for default visualizations or diagrams.
Prefer Graphviz DOT in one fenced ```dot block for relationships, architecture, workflows, and dense diagrams.
Use Vega-Lite JSON in one fenced ```vega-lite block for data charts.
Only use Mermaid when the user explicitly asks for Mermaid or selects Mermaid during visualization regeneration."""

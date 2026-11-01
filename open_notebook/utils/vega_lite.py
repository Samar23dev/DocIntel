from langchain_core.messages import HumanMessage

VEGA_LITE_INSTRUCTION = """# VEGA-LITE CHART SPECIALIST
When the user requests a data chart, produce one valid JSON object in a fenced ```vega-lite code block.
Use Vega-Lite v5 syntax. Include a schema, mark type, data values, encoding, and useful titles.
Prefer a concise declarative specification with no JavaScript, expressions, network requests, local files, or embedded HTML.
Use quoted string values for temporal, nominal, and ordinal encodings.
Use numeric values and field names that match the supplied source data.
Keep labels concise and include units in axis titles where applicable."""


def vega_lite_instruction_for_messages(messages: list) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = message.content if isinstance(message.content, str) else str(message.content)
            normalized = text.lower()
            chart_terms = (
                "chart", "graph", "histogram", "scatter", "bar", "line",
                "pie", "trend", "timeline", "comparison",
            )
            chart_request = any(word in normalized for word in (
                "create", "draw", "generate", "make", "show", "plot", "visualize",
            ))
            if any(term in normalized for term in chart_terms) and chart_request:
                return VEGA_LITE_INSTRUCTION
            return None

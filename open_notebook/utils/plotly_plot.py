from langchain_core.messages import HumanMessage

PLOTLY_INSTRUCTION = """# PLOTLY SPECIALIST
When the user explicitly requests Plotly or selects Plotly during visualization regeneration, produce one complete executable Python block using the ```plotly-plot fence. Assign the finished Plotly Figure to a variable named fig. Use plotly.express or plotly.graph_objects. Do not save files, call fig.show(), access the network, or use imports outside Plotly, NumPy, pandas, and standard library modules. The application renders fig automatically."""


def plotly_instruction_for_messages(messages: list) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = message.content if isinstance(message.content, str) else str(message.content)
            normalized = text.lower()
            if "plotly" in normalized and any(word in normalized for word in ("plotly", "chart", "graph", "plot", "regenerate")):
                return PLOTLY_INSTRUCTION
            return None
    return None

from langchain_core.messages import HumanMessage

MERMAID_INSTRUCTION = """# MERMAID DIAGRAM SPECIALIST
When the user asks for a Mermaid diagram or a visual/diagram representation, produce valid Mermaid source in one fenced ```mermaid code block. Use a diagram type supported by Mermaid (flowchart, sequenceDiagram, classDiagram, erDiagram, stateDiagram-v2, gantt, mindmap, journey, or pie). Do not use HTML, JavaScript, or executable directives. Keep labels concise and ensure every node and relationship is consistent with the supplied data. If you also explain the diagram, place the Mermaid block after a short explanation."""


def mermaid_instruction_for_messages(messages: list) -> str | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = message.content if isinstance(message.content, str) else str(message.content)
            normalized = text.lower()
            if (
                "mermaid" in normalized
                or "flowchart" in normalized
                or "sequence diagram" in normalized
                or "class diagram" in normalized
                or "entity relationship" in normalized
                or " er diagram" in normalized
                or "state diagram" in normalized
                or "mind map" in normalized
                or ("diagram" in normalized and any(word in normalized for word in ("create", "draw", "generate", "make", "visualize", "show")))
            ):
                return MERMAID_INSTRUCTION
            return None
    return None

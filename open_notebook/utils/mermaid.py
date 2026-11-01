MERMAID_INSTRUCTION = """# MERMAID VERSION
This application renders Mermaid diagrams with Mermaid 11.17.2. Produce Mermaid syntax that is supported by Mermaid 11.17.2 in one fenced ```mermaid block.
Choose the most appropriate Mermaid diagram type yourself based on the requested visual.
Do not add renderer configuration, HTML, JavaScript, CSS, executable directives, or explanations inside the Mermaid block. Keep labels concise and accurate."""


def mermaid_instruction_for_messages(messages: list) -> str | None:
    return None

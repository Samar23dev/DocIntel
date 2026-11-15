# DocIntel Architecture

This document describes DocIntel's runtime, processing, AI, storage, and visualization flows.

```mermaid
flowchart TB
    user([User / Browser])

    subgraph frontend[Next.js Frontend :8502]
        ui[Notebook and Source UI]
        chat[Chat and Markdown Viewer]
        localization[14 Interface Locales]
        visualization[Visualization Markdown Dispatcher]
        mplrender[Matplotlib SVG Viewer]
        plotlyrender[Plotly.js Viewer]
        vegarender[Vega-Embed Viewer]
        dotrender[Graphviz WASM Viewer]
        mermaidrender[Mermaid Viewer]
    end

    subgraph application[DocIntel Application Container]
        api[FastAPI REST API :5055]
        auth[Authentication and Credentials]
        workers[Background Workers]

        subgraph processing[Source Processing]
            ingest[Upload and Source Intake]
            extractor[Text and Document Extraction]
            docling[Optional Docling OCR and Layout]
            embeddings[Embedding Generation]
        end

        subgraph ai[AI Orchestration]
            graphs[Notebook, Source, Search, and Transformation Graphs]
            context[Context Assembly and Retrieval]
            dotagent[Graphviz DOT Specialist]
            mplagent[Matplotlib Specialist]
            plotlyagent[Explicit Plotly Specialist]
            vegaagent[Explicit Vega-Lite Specialist]
            mermaidagent[Explicit Mermaid Specialist]
        end

        subgraph visualization_api[Visualization Services]
            mplapi["POST /api/python/plot"]
            plotlyapi["POST /api/python/plotly"]
            pythonexec[Restricted Python Plot Execution]
            svgcheck[SVG Validation and Sanitization]
            figurejson[Plotly Figure JSON]
        end
    end

    subgraph storage[Persistent Storage]
        database[(SurrealDB :8000)]
        files[/notebook_data/<br/>Uploads and Runtime Cache/]
        vectors[(Stored Embeddings and Records)]
    end

    subgraph providers[External AI Providers]
        cloud[Cloud LLM, Embedding, STT, and Vision Providers]
        local[Local Providers, such as Ollama]
    end

    user --> frontend
    ui --> api
    chat --> api
    visualization --> api

    api --> auth
    api --> ingest
    api --> workers
    workers --> ingest

    ingest --> extractor
    extractor --> docling
    docling --> embeddings
    embeddings --> database
    ingest --> files

    api --> graphs
    graphs --> context
    context --> database
    database --> vectors
    graphs --> cloud
    graphs --> local

    chat --> dotagent
    chat --> mplagent
    chat --> plotlyagent
    chat --> vegaagent
    chat --> mermaidagent
    dotagent --> visualization
    mplagent --> visualization
    plotlyagent --> visualization
    vegaagent --> visualization
    mermaidagent --> visualization

    visualization -->|python-plot fence| mplapi
    visualization -->|plotly-plot fence| plotlyapi
    mplapi --> pythonexec
    plotlyapi --> pythonexec
    pythonexec --> svgcheck
    pythonexec --> figurejson
    svgcheck --> mplrender
    figurejson --> plotlyrender
    visualization -->|vega-lite fence| vegarender
    visualization -->|dot fence| dotrender
    visualization -->|mermaid fence| mermaidrender

    database --> api
    files --> extractor
    api --> database
    api --> frontend
```

## Runtime flow

1. The browser uses the Next.js interface to create notebooks, upload sources, manage settings, and chat.
2. FastAPI validates requests and routes them to application endpoints or background workers.
3. Source processing extracts text, tables, and document structure from PDF, DOCX, XLSX, URLs, text, and supported media.
4. Optional Docling processing adds layout analysis and OCR for scanned PDFs and images.
5. A configured embedding model converts extracted text into vectors for semantic search and retrieval. Embeddings are persisted in SurrealDB.
6. AI graphs combine retrieved context with a configured language, embedding, and chat model before returning streamed responses.
7. Visualization format policy selects Matplotlib for default data charts and Graphviz DOT for default relationship, workflow, and architecture diagrams. Plotly, Vega-Lite, and Mermaid are generated when explicitly requested or selected from regeneration.
8. The Markdown dispatcher sends Matplotlib and Plotly Python blocks to separate FastAPI endpoints. Matplotlib returns SVG; Plotly returns figure JSON for browser-side Plotly.js rendering. Vega-Lite, DOT, and Mermaid render locally with Vega-Embed, Graphviz WASM, and Mermaid respectively.
9. Local files and runtime state remain under `notebook_data/`; SurrealDB records remain under `surreal_data/`.

## Visualization formats

| Format | Default or selection | Render path |
| --- | --- | --- |
| Matplotlib/Python | Default for data charts | Python execution through `/api/python/plot`; backend returns SVG for the frontend |
| Graphviz DOT | Default for relationships, workflows, and architecture diagrams | Browser-side Graphviz WASM renderer |
| Plotly/Python | Explicit request or regeneration | Python execution through `/api/python/plotly`; backend returns figure JSON for Plotly.js |
| Vega-Lite | Explicit request or regeneration | Browser-side `vega-embed` compilation and rendering |
| Mermaid | Explicit request or regeneration | Browser-side Mermaid rendering |

Generated visualizations are returned as fenced Markdown blocks. The frontend dispatches each recognized fence to its format-specific renderer and exposes format-appropriate source and image export controls. Regeneration sends the selected target format back through chat.

## OCR flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Next.js Settings
    participant API as FastAPI
    participant Worker as Source Worker
    participant Engine as Content Extraction Engine
    participant Docling as Optional Docling Runtime
    participant DB as SurrealDB

    User->>UI: Upload scanned PDF and enable OCR
    UI->>API: Create source and processing settings
    API->>Worker: Start background processing job
    Worker->>Engine: Extract source using selected engine

    alt Docling is enabled
        Engine->>Docling: Detect layout and OCR text pages
        Docling-->>Engine: Paragraphs, tables, reading order, and OCR text
    else Simple extraction is selected
        Engine-->>Worker: Native or lightweight text extraction
    end

    Worker->>DB: Store extracted content and metadata
    opt Embeddings are enabled
        Worker->>DB: Generate and store vectors
    end
    Worker-->>API: Processing complete
    API-->>UI: Show processed source and extracted content
```

## Multilingual flow

```mermaid
flowchart LR
    browser[Browser Locale] --> detector[i18next Language Detector]
    detector --> local[localStorage Preference]
    detector --> navigator[Navigator Language]
    local --> ui[Translated Next.js Interface]
    navigator --> ui
    ui --> fallback[English fallback]

    sources[Multilingual Source Text] --> extraction[Extraction and Optional OCR]
    extraction --> embeddings[Configured Embedding Model]
    embeddings --> vectors[(Language-Aware Vector Retrieval)]
    vectors --> llm[Configured Chat or Generation Model]
    llm --> response[Localized Summary, Chat, or Transformation]
```

## Security boundaries

- Provider credentials are encrypted by the application using the configured encryption key.
- `.env`, uploads, databases, credentials, caches, and runtime data must not be committed.
- Mermaid uses strict rendering mode and generated SVG output is sanitized before browser insertion.
- Python chart requests use AST checks, import restrictions, code/output limits, a timeout, and temporary working directories. Plotly figure data is serialized to JSON and rendered by the local Plotly.js package.
- Python chart execution uses process-level restrictions and is not a fully isolated sandbox for arbitrary untrusted code.

For setup and operational instructions, see [README.md](README.md).

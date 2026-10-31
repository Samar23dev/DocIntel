# DocIntel Architecture

This diagram describes the main runtime, processing, AI, and storage flows in DocIntel.

```mermaid
flowchart TB
    user([User / Browser])

    subgraph frontend[Next.js Frontend :8502]
        ui[Notebook and Source UI]
        chat[Chat and Markdown Viewer]
        localization[14 Interface Locales]
        visualization[Mermaid and Matplotlib Rendering]
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
            mermaid[Mermaid Specialist]
            pythonplot[Matplotlib Specialist]
        end

        subgraph visualization_api[Visualization Services]
            plotapi[Restricted Python Plot API]
            sanitizer[SVG Sanitization and Download Support]
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

    chat --> mermaid
    chat --> pythonplot
    mermaid --> api
    pythonplot --> plotapi
    plotapi --> sanitizer
    sanitizer --> visualization

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
7. Mermaid specialist output is rendered as SVG in Markdown. Matplotlib specialist output is executed by the restricted plot API, sanitized, and rendered in Markdown.
8. Local files and runtime state remain under `notebook_data/`; SurrealDB records remain under `surreal_data/`.

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
- Python plotting restricts imports, dynamic execution, file access, private attributes, execution time, code size, and SVG size.
- Python plot execution currently uses process-level restrictions and is not an unrestricted untrusted-code sandbox.

For setup and operational instructions, see [README.md](README.md).

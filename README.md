# AI Research Agent

A command-line research assistant that combines local PDF retrieval with web search. It routes questions to the PDF collection, the web, or both, then creates a cited report. Reports can be exported as PDFs, and query history is stored locally in SQLite.

## Features

- **Source routing:** selects PDF-only, web-only, or combined research based on the query and conversation context.
- **PDF retrieval:** extracts PDF text, chunks and embeds it with `all-MiniLM-L6-v2`, stores it in ChromaDB, and retrieves relevant passages.
- **Web research:** creates search tasks and searches with Tavily.
- **Cited reports:** Groq generates reports with inline web (`[S1]`) and PDF (`[P1]`) citations, followed by citation checks.
- **Conversation context:** follow-up questions can use earlier turns in the current CLI session.
- **Local history and export:** saves research history in SQLite and exports reports with ReportLab.

## How it works

```text
Question -> OpenRouter intent detection and planning
          -> PDF_ONLY: ChromaDB retrieval ----------------+
          -> WEB_ONLY: plan -> Tavily search ------------+-> Groq report
          -> PDF_AND_WEB: PDF retrieval + web search -----+      -> CLI / PDF export
                                                                -> SQLite history
```

## Technology

| Area | Technology |
| --- | --- |
| Workflow | LangGraph |
| Intent detection and planning | OpenRouter via LangChain `ChatOpenAI` |
| Report generation | Groq (`llama-3.3-70b-versatile`) |
| Web search | Tavily |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB |
| PDF reading / writing | pdfplumber / ReportLab |
| History | SQLite |

## Requirements

- Python 3.12 or newer
- API keys for OpenRouter, Groq, and Tavily
- `uv` recommended for dependency installation

## Setup

```bash
git clone https://github.com/<your-username>/Ai-Research-Agent.git
cd Ai-Research-Agent
uv sync
```

Create a `.env` file in the project root (or copy `.env.example`) with:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
GROQ_API=your_groq_api_key
TAVILY_API=your_tavily_api_key
```

Get keys from [OpenRouter](https://openrouter.ai/), [Groq](https://console.groq.com/), and [Tavily](https://tavily.com/). Keep `.env` private; never commit API keys.

## Run

```bash
uv run python -m app.main
```

Enter a research question. Type `save pdf` to export the latest report, or `exit` to end the session. An unsaved report is exported when the session exits.

Example questions:

```text
Explain residual learning from the uploaded PDF
What is the latest research on residual learning?
Compare the uploaded PDF with recent research on residual learning
Explain this simply
```

## Add a PDF to the local index

The ingestion script currently uses `tests/Research_Paper.pdf` as its sample input. To index it:

```bash
uv run python -m tests.test_vector
```

To ingest another document, change `pdf_path` in `tests/test_vector.py`. This creates/updates the local `chroma_db/` directory. The sample PDF is for demonstration; the ChromaDB index and SQLite history are local data and are not required in a GitHub clone.

## Project layout

```text
app/
  main.py                 Interactive CLI
  graph/                  LangGraph state, nodes, and routing
  planner/                OpenRouter intent detection and planning
  llm/                    Groq report generation and prompts
  tools/                  PDF loading, chunking, embeddings, retrieval, search
  database/               SQLite research history
  utils/                  PDF report generation
tests/                    Manual scripts and sample PDF
```

## Configuration and local files

The app reads `OPENROUTER_API_KEY`, `GROQ_API`, and `TAVILY_API` from the environment. Sentence Transformers downloads its embedding model on first use. Generated reports, the ChromaDB index, and `research_history.db` are local artifacts.

## License

No `LICENSE` file is currently included. Add the license you intend to use before presenting the repository as open source under a specific license.

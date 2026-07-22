# AI Research & Browser Agent — Full Project Plan

## 1. Project Overview

**What it is:** An AI agent that takes a research query from the user, plans out how to answer it, searches the web across multiple sources, reads and compares information (including PDFs), synthesizes a report with citations, and exports the final output as a PDF. It also saves research history so past queries can be revisited.

**Why it's a strong project:** Unlike a basic chatbot or plain RAG app, this project demonstrates agent orchestration — the system plans multi-step tasks, decides which tool to use when, and combines retrieval with reasoning. This maps directly to what companies mean by "agentic AI" right now.

**Example flow:**
```
User: "Compare Groq vs OpenAI vs Gemini for production RAG"
   ↓
Agent:
  1. Plans the research (breaks query into sub-questions)
  2. Searches the web for each sub-question
  3. Reads/compares multiple sources
  4. Summarizes findings with source citations
  5. Generates a structured final report
  6. Exports as PDF
  7. Saves to research history
```

---

## 2. Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| LLM | Groq (`llama-3.3-70b-versatile` via OpenAI-compatible API) | Reasoning, summarization, report generation |
| Agent orchestration | LangGraph | State graph for planning → searching → synthesizing steps |
| Web search | Tavily (or DuckDuckGo as free fallback) | Live web search results |
| Vector DB | ChromaDB | Store/retrieve embedded content from PDFs and past research |
| PDF reading | `pdfplumber` or `PyPDF2` | Extract text from uploaded/found PDFs |
| PDF export | `reportlab` or `fpdf2` | Generate the final report as a downloadable PDF |
| History storage | SQLite (or simple JSON initially) | Save past research sessions |
| (Later, optional) | MCP, Firecrawl | Advanced tool integration, better web scraping — add only after core is working |

---

## 3. Prerequisites Before Building

- [x] Python fundamentals (functions, classes, decorators, dicts, try/except) — you've completed this
- [x] Understand LLM API calls (Groq chat completions, system/user roles)
- [x] Understand tool-calling / function-calling concept (HF Agents Unit 1)
- [ ] Understand LangGraph basics (nodes, edges, state)
- [x] Get free API keys: Groq (console.groq.com) and Tavily (tavily.com)

---

## 4. Build Plan — Step by Step

### **Phase 1: Bare-bones search + summarize (no framework yet)**
Goal: prove the core loop works before adding any complexity.

1. Set up a Python project folder, virtual environment, `.env` file for API keys
2. Write a function that calls Tavily with a search query, returns raw results (title, snippet, URL)
3. Write a function that sends those results + the original query to Groq, asks it to summarize
4. Connect them: `user query → search() → summarize() → print result`
5. Test with 3-4 different queries, fix any breakage

**Deliverable:** A CLI script where you type a question and get a summarized, source-aware answer.

---

### **Phase 2: Add LangGraph orchestration**
Goal: turn the linear script into a proper agent graph.

1. Define the agent's state (what data flows between steps: query, search results, sources, draft summary)
2. Create nodes: `plan_node` (breaks query into sub-questions), `search_node`, `summarize_node`
3. Wire nodes together with edges — decide if any conditional routing is needed (e.g., re-search if results are poor)
4. Replace your Phase 1 script's logic with this graph
5. Test again with the same queries — output should be more structured now

**Deliverable:** Same CLI script, but now powered by a LangGraph agent instead of a linear function chain.

---

### **Phase 3: Multi-source comparison**
Goal: handle queries where several distinct things need comparing (like the Groq vs OpenAI vs Gemini example).

1. Update the planning step to detect when a query has multiple entities to compare
2. Run parallel or sequential searches for each entity
3. Update the summarize step to produce a structured comparison (table-like format) instead of plain prose

**Deliverable:** Agent can handle "Compare X vs Y vs Z" style queries distinctly from single-topic queries.

---

### **Phase 4: PDF reading (RAG piece)**
Goal: let the agent read and use PDF content, not just web pages.

1. Add a PDF upload/ingestion function using `pdfplumber`
2. Chunk the extracted text (e.g., 500-token chunks with overlap)
3. Generate embeddings for each chunk, store in ChromaDB
4. Add a `retrieve_node` to the graph — when relevant, pull matching chunks from ChromaDB instead of (or alongside) web search
5. Test with a sample PDF (e.g., a research paper) and ask questions about it

**Deliverable:** Agent can answer questions using both live web search AND previously uploaded PDFs.

---

### **Phase 5: Source citations**
Goal: every claim in the final answer should be traceable to a source.

1. When storing search/PDF results, keep track of source URL/filename alongside the content
2. Update the summarize/report prompt to require citing sources inline (e.g., "[Source: URL]")
3. Validate output — check that citations actually correspond to real retrieved sources (avoid hallucinated citations)

**Deliverable:** Final report includes clear source attribution for each major claim.

---

### **Phase 6: Report generation + PDF export**
Goal: turn the agent's raw output into a polished, downloadable report.

1. Design a simple report structure (title, executive summary, detailed comparison/findings, sources list)
2. Write a function using `reportlab` (or `fpdf2`) that takes the structured output and renders it as a PDF
3. Test export with a full end-to-end run

**Deliverable:** Running the agent produces a downloadable PDF report, not just terminal text.

---

### **Phase 7: Research history**
Goal: save and revisit past research sessions.

1. Set up SQLite (or JSON file) with a simple schema: query, timestamp, summary, sources, PDF path
2. Add a save function that runs at the end of each research session
3. Add a simple list/retrieve function so past sessions can be viewed again

**Deliverable:** Agent maintains a history of everything it has researched.

---

### **Phase 8 (Optional, only if time permits before interviews): Polish**
- Add a simple UI (Streamlit or a basic HTML/React frontend) instead of CLI only
- Add MCP tool integration
- Add Firecrawl for better web scraping than basic search snippets
- Deploy the app (Render/Railway) so you have a live demo link

---

## 5. What to Be Able to Explain in Interviews

For each phase above, know:
- **Why** you made that design choice (e.g., "why LangGraph over just prompting the LLM to plan?")
- **One bug** you hit and how you fixed it
- **One trade-off** you made (e.g., "why ChromaDB over Pinecone?" → local, free, simple for a student project)
- **What you'd improve** if you had more time — shows maturity, always a good answer to "limitations?"

---

## 6. Suggested Time Estimate

| Phase | Est. Time |
|---|---|
| Phase 1 | 3-4 hrs |
| Phase 2 | 4-5 hrs |
| Phase 3 | 2-3 hrs |
| Phase 4 | 4-5 hrs |
| Phase 5 | 2 hrs |
| Phase 6 | 3 hrs |
| Phase 7 | 2 hrs |
| Phase 8 (optional) | flexible |
| **Total (core, Phases 1-7)** | **~20-24 hrs** |

At roughly 1.5-2 hrs/day (your evening project slots), this is realistically a **2-3 week build**, which fits your timeline well since Job Application Tracker starts after this.

---

## 7. Resources Mapped to Each Phase

- **Phase 1-2 (agent basics, LangGraph):** https://www.youtube.com/watch?v=Hz21KVo0t4E
- **Tool-calling concept:** https://huggingface.co/learn/agents-course/en/unit1/tutorial
- **smolagents patterns (alternative reference):** https://www.youtube.com/watch?v=dSGS6-iGhyo
- **Groq API docs:** console.groq.com → Docs → Quickstart
- **Tavily API docs:** tavily.com → Docs → Quickstart
- **ChromaDB quickstart:** docs.trychroma.com (getting started guide)

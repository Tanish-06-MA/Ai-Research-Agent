import os
import re
from app.llm.prompts import SYSTEM_PROMPT
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API"))


def _build_source_map(search_results, documents):
    source_map = {}
    url_to_id = {}
    web_sources = []

    for task_data in search_results:
        for result in task_data.get("results", []):
            url = result.get("url")
            if not url:
                continue
            if url not in url_to_id:
                source_id = f"S{len(url_to_id) + 1}"
                url_to_id[url] = source_id
                source_map[source_id] = url
                web_sources.append(
                    {
                        "id": source_id,
                        "title": result.get("title", "Untitled"),
                        "snippet": result.get("snippet", ""),
                        "url": url,
                    }
                )

    pdf_sources = {}
    pdf_source_list = []
    for document in documents or []:
        source = document.get("source", "Unknown PDF")
        content = document.get("content", "")
        if source not in pdf_sources:
            pdf_id = f"P{len(pdf_sources) + 1}"
            pdf_sources[source] = pdf_id
            source_map[pdf_id] = source
            pdf_source_list.append({"id": pdf_id, "source": source, "chunks": []})

        for entry in pdf_source_list:
            if entry["source"] == source:
                entry["chunks"].append(content)
                break

    return source_map, web_sources, pdf_source_list


def _strip_sources_section(report_text):
    return re.split(r"\n##\s*Sources\b", report_text, flags=re.IGNORECASE, maxsplit=1)[
        0
    ].strip()


def _find_citations(report_text):
    return re.findall(r"\[(S\d+|P\d+)\]", report_text)


def _remove_invalid_citations(report_text, invalid_ids):
    for invalid_id in invalid_ids:
        report_text = report_text.replace(f"[{invalid_id}]", "")
    return report_text


def _sort_source_ids(source_ids):
    def key(source_id):
        prefix = 0 if source_id.startswith("S") else 1
        return (prefix, int(source_id[1:]))

    return sorted(set(source_ids), key=key)


def _format_sources_section(source_ids, source_map):
    lines = ["## Sources"]
    for source_id in _sort_source_ids(source_ids):
        lines.append(f"[{source_id}] {source_map[source_id]}")
    return "\n".join(lines)


def _is_generic_paragraph(paragraph):
    normalized = paragraph.strip()
    if len(normalized) < 120 and re.match(
        r"^(This report|This document|In this report|Overall|In summary|To begin|To conclude|The following|Additionally|Also|Moreover|Furthermore|Next|Finally|As a result|Therefore)",
        normalized,
        flags=re.IGNORECASE,
    ):
        return True
    return False


def _has_factual_language(paragraph):
    return bool(
        re.search(
            r"\b(is|are|was|were|has|have|uses|utilizes|provides|describes|explains|states|reports|shows|finds|based on|according to|supports|studies|findings|results|research|paper|model|architecture)\b",
            paragraph,
            flags=re.IGNORECASE,
        )
    )


def _count_uncited_factual_paragraphs(report_text):
    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", report_text)
        if paragraph.strip()
    ]

    uncited = 0
    for paragraph in paragraphs:
        if paragraph.startswith("#"):
            continue
        if paragraph.startswith("-") or paragraph.startswith("*"):
            continue
        if _find_citations(paragraph):
            continue
        if _is_generic_paragraph(paragraph):
            continue
        if _has_factual_language(paragraph):
            uncited += 1

    return uncited


def _repair_report(report_text, web_sources, pdf_sources):
    source_reference = ""
    if web_sources:
        source_reference += "Web Source Reference Data:\n"
        for source in web_sources:
            source_reference += f"\nSOURCE ID: [{source['id']}]\nTitle: {source['title']}\nContent:\n{source['snippet']}\nURL: {source['url']}\n---\n"
    if pdf_sources:
        source_reference += "\nPDF Source Reference Data:\n"
        for pdf in pdf_sources:
            combined_chunks = "\n\n".join(pdf["chunks"]).strip()
            source_reference += f"\nPDF SOURCE ID: [{pdf['id']}]\nPDF Content:\n{combined_chunks}\nPDF Source:\n{pdf['source']}\n---\n"

    repair_prompt = f"""
The report below is missing inline citations or has invalid citations.
Insert valid citations using only the provided source IDs.
Do not invent new source IDs or URLs.
Do not add a Sources section.
Do not change the factual meaning of the report.

Report:
{report_text}

{source_reference}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": repair_prompt},
        ],
    )

    return _strip_sources_section(response.choices[0].message.content)


def generate_summary(query, plan, search_results, documents, conversation_history=""):
    source_map, web_sources, pdf_sources = _build_source_map(search_results, documents)

    prompt = f"""
You are generating a research report.

IMPORTANT CITATION RULES:

1. Every major factual claim MUST have a citation.
2. Web sources must use [S1], [S2], [S3], etc.
3. PDF sources must use [P1], [P2], [P3], etc.
4. Use ONLY the source IDs provided below.
5. Never invent or renumber source IDs.
6. Never invent URLs or PDF source paths.
7. Put each citation immediately after its factual claim.
8. Do not cite a source unless it supports the claim.
9. Do not generate a Sources section. Python will append it automatically.

If a web source is unrelated to the research topic, IGNORE it.

Do not create sections such as Pricing, Cost, Benchmarking,
or other topics unless they are explicitly relevant to the user query.

If the user asks to compare an uploaded PDF with web sources:
- Use the PDF as the primary document source.
- Clearly separate PDF findings from web findings.
- Only compare information that is actually supported by the PDF and relevant web sources.
- Do not force information from unrelated web sources into the report.
- If the PDF does not contain enough information to answer a part of the query, explicitly say so.

Previous Conversation:
{conversation_history if conversation_history else "No previous conversation."}

User Query:
{query}

Research Plan:
{plan}

Search Tasks:
"""

    for task_data in search_results:
        task = task_data.get("task")
        results = task_data.get("results", [])

        prompt += f"\nResearch Task: {task}\n"
        if not results:
            prompt += "- No search results found for this task.\n"
            continue

        for result in results:
            url = result.get("url", "No URL")
            source_id = next(
                (source["id"] for source in web_sources if source["url"] == url),
                "Unknown",
            )
            prompt += f"- [{source_id}] {result.get('title', 'Untitled')} ({url})\n"

    prompt += "\nSOURCE REFERENCE DATA:\n"
    if web_sources:
        for source in web_sources:
            prompt += f"\nSOURCE ID: [{source['id']}]\nTitle: {source['title']}\nContent:\n{source['snippet']}\nURL: {source['url']}\n---\n"
    else:
        prompt += "No web sources available.\n"

    if pdf_sources:
        prompt += "\nPDF SOURCE REFERENCE DATA:\n"
        for pdf in pdf_sources:
            combined_chunks = "\n\n".join(pdf["chunks"]).strip()
            prompt += f"\nPDF SOURCE ID: [{pdf['id']}]\nPDF Content:\n{combined_chunks}\nPDF Source:\n{pdf['source']}\n---\n"
    else:
        prompt += "\nNo PDF sources available.\n"

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    report = _strip_sources_section(chat_completion.choices[0].message.content)

    citations = _find_citations(report)
    valid_citations = [citation for citation in citations if citation in source_map]
    invalid_citations = [
        citation for citation in citations if citation not in source_map
    ]

    if invalid_citations:
        print(f"WARNING: Invalid citations removed: {sorted(set(invalid_citations))}")
        report = _remove_invalid_citations(report, sorted(set(invalid_citations)))
        citations = _find_citations(report)
        valid_citations = [citation for citation in citations if citation in source_map]

    if not valid_citations and source_map:
        print(
            "WARNING: No citations were generated by the LLM. Attempting citation repair."
        )
        repaired_report = _repair_report(report, web_sources, pdf_sources)
        repaired_citations = _find_citations(repaired_report)
        repaired_valid = [
            citation for citation in repaired_citations if citation in source_map
        ]
        if repaired_valid:
            report = repaired_report
            valid_citations = repaired_valid
            citations = repaired_citations
        else:
            print("WARNING: Citation repair did not produce valid inline citations.")

    uncited = _count_uncited_factual_paragraphs(report)
    print("Citation validation:")
    print(f"Total citations: {len(citations)}")
    print(f"Valid citations: {len(valid_citations)}")
    print(f"Invalid citations: {len(invalid_citations)}")
    print(f"Uncited factual paragraphs: {uncited}")

    final_report = report.strip()
    if valid_citations:
        final_report += "\n\n" + _format_sources_section(valid_citations, source_map)

    return final_report

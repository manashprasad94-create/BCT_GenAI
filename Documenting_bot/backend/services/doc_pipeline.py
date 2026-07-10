import os
import concurrent.futures
from services.groq_client import groq_client, MODEL, summarize_file
from services.file_filter import build_tree_string

MAX_WORKERS = 5  # concurrency cap, respects Groq rate limits
MAX_FILES_TO_SUMMARIZE = 60  # safety cap for very large repos (v1 limit)

REDUCE_SYSTEM_PROMPT = (
    "You are a senior technical writer producing professional project documentation. "
    "You will be given a project's file tree and per-file summaries. "
    "Write complete Markdown documentation with these sections, in this order:\n"
    "1. Overview — what the project does, in plain language\n"
    "2. Tech Stack — languages, frameworks, key libraries detected\n"
    "3. Architecture — how the major pieces fit together. Include a Mermaid "
    "flowchart diagram showing how the main components/modules interact, using "
    "this exact format:\n"
    "```mermaid\n"
    "flowchart TD\n"
    "    A[Component Name] --> B[Another Component]\n"
    "```\n"
    "Base the diagram strictly on the actual files and their relationships from "
    "the summaries provided — do not invent components that don't exist.\n"
    "4. Folder Structure — brief explanation of key folders/files\n"
    "5. Setup & Installation — inferred steps to install and run the project\n"
    "6. Key Modules — the most important files/classes/functions and what they do\n"
    "7. Usage — how someone would use or run this project\n\n"
    "Be factual based only on what's given. If something is unclear, say so briefly "
    "rather than inventing details. Use proper Markdown headers and formatting. "
    "The Mermaid diagram must use valid Mermaid flowchart syntax exactly as shown above."
)


def _summarize_one(file_info: dict) -> dict:
    """Reads and summarizes a single file. Returns dict with path + summary."""
    try:
        with open(file_info["absolute_path"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        summary = summarize_file(file_info["relative_path"], content)
    except Exception as e:
        summary = f"(Could not summarize: {e})"

    return {"path": file_info["relative_path"], "summary": summary}


def run_map_step(files: list[dict]) -> list[dict]:
    """Runs summarize_file across all files concurrently."""
    files_to_process = files[:MAX_FILES_TO_SUMMARIZE]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(_summarize_one, f) for f in files_to_process]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results


def run_reduce_step(project_root: str, tree_string: str, summaries: list[dict]) -> str:
    """Takes all file summaries + tree, produces the final documentation."""
    summaries_text = "\n\n".join(
        f"### {s['path']}\n{s['summary']}" for s in summaries
    )

    user_prompt = (
        f"Project file tree:\n```\n{tree_string}\n```\n\n"
        f"Per-file summaries:\n{summaries_text}"
    )

    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REDUCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=3000,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def generate_documentation(project_root: str, files: list[dict]) -> str:
    """Full pipeline: map step -> reduce step -> final markdown doc."""
    tree_string = build_tree_string(project_root, files)
    summaries = run_map_step(files)
    final_doc = run_reduce_step(project_root, tree_string, summaries)
    return final_doc
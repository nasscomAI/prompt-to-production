"""
UC-X app.py — "Ask My Documents"

Implements the two skills defined in skills.md:

  - retrieve_documents(): deterministic, non-AI. Loads the three fixed
    policy files and builds a structured index of sections.
  - answer_question(question, documents): the only LLM-calling skill.
    Relays the model's cited answer or refusal-template response.

...and the interactive CLI loop described in README.md.

See agents.md for the enforcement rules the system prompt (system_prompt.md)
implements, and skills.md for the exact input/output/error-handling
contracts for each skill.
"""

import os
import re
import sys

import anthropic
from dotenv import load_dotenv

# Loads ANTHROPIC_API_KEY (and any other vars) from a .env file. Uses
# python-dotenv's default upward search, which finds the repo-root .env
# regardless of the current working directory this script is run from.
load_dotenv()

APP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(APP_DIR)

POLICY_DIR = os.path.join(REPO_ROOT, "data", "policy-documents")

# The fixed set of three source-of-truth documents (agents.md "role").
POLICY_DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# system_prompt.md lives alongside app.py; loaded at runtime, never
# hardcoded into this file (per skills.md's answer_question contract).
SYSTEM_PROMPT_PATH = os.path.join(APP_DIR, "system_prompt.md")

# Deliberately the lighter Haiku 4.5 model for this UC, per an explicit
# earlier decision — not claude-sonnet-5 / claude-opus-*.
MODEL_NAME = "claude-haiku-4-5-20251001"

# Reproduced verbatim from agents.md / skills.md / README.md. Must never
# be reworded, trimmed, or have anything appended/prepended when used.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# A distinct, clearly-labeled system-level error, kept deliberately
# different in wording and shape from REFUSAL_TEMPLATE so a knowledge-base
# failure is never confused with an ordinary "not covered" policy refusal
# (skills.md, answer_question error_handling).
KNOWLEDGE_BASE_UNAVAILABLE_MESSAGE = (
    "SYSTEM ERROR: the policy document knowledge base is unavailable "
    "(retrieve_documents did not return a complete set of documents). "
    "This question cannot be answered because the source documents "
    "could not be loaded — this is not a policy refusal."
)

# Detects a numbered clause marker such as "2.6" at the start of a line,
# e.g. "2.6 Employees may carry forward ...". Clause markers are the
# section boundaries we index on (skills.md: "keyed by ... section
# number"; README/agents.md examples all cite "<document>, Section X.X").
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")

# Detects a top-level heading such as "2. ANNUAL LEAVE" (a single number,
# a dot, then whitespace before the title — as opposed to a clause marker
# like "2.6 ..." which has a second digit immediately after the dot).
# Headings are never indexed as their own section; they only supply a
# human-readable section_title for the clauses that follow them.
HEADING_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")


class DocumentLoadError(Exception):
    """Raised by retrieve_documents() when the fixed document set cannot
    be fully loaded. Fatal by design — see skills.md: a partial index
    would make it impossible to correctly distinguish "not covered" from
    "covered by the missing document"."""


def _is_decorative(line):
    """True for a pure box-drawing/rule line (e.g. a row of '=' or '═')
    with no alphanumeric content — layout noise to be skipped rather than
    folded into a clause's section_text or the unsectioned fallback."""
    return bool(line) and not any(ch.isalnum() for ch in line)


def _parse_sections(document_name, text):
    """
    Split one policy document's raw text into an ordered list of
    {document_name, section_number, section_title, section_text} dicts.

    Section boundaries are detected via "<n>.<n>" clause markers (e.g.
    "2.6 ..."), the same general technique used for clause parsing
    elsewhere, adapted to these three documents' numbering. Top-level
    headings ("2. ANNUAL LEAVE") are tracked only to label subsequent
    clauses with a section_title; they are never themselves indexed as a
    section and no section_number is ever invented that isn't literally
    present in the source text.

    If nothing in the document matches the clause pattern, the entire
    document is indexed under a single fallback section with
    section_number "unsectioned" rather than being dropped.
    """
    sections = []
    current_title = None
    current_number = None
    current_lines = []
    preamble_lines = []

    def flush():
        if current_number is not None:
            body = "\n".join(current_lines).strip()
            if body:
                sections.append({
                    "document_name": document_name,
                    "section_number": current_number,
                    "section_title": current_title,
                    "section_text": body,
                })

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or _is_decorative(line):
            continue

        clause_match = CLAUSE_RE.match(line)
        heading_match = None if clause_match else HEADING_RE.match(line)

        if clause_match:
            flush()
            current_number = clause_match.group(1)
            current_lines = [line]
        elif heading_match:
            current_title = heading_match.group(2).strip()
        elif current_number is not None:
            current_lines.append(line)
        else:
            preamble_lines.append(line)

    flush()

    if not sections:
        full_text = "\n".join(preamble_lines).strip() or text.strip()
        return [{
            "document_name": document_name,
            "section_number": "unsectioned",
            "section_title": None,
            "section_text": full_text,
        }]

    return sections


def retrieve_documents():
    """
    Deterministic, non-AI loading step (skills.md: retrieve_documents).

    Reads the three fixed policy files from disk and returns a document
    index: a dict keyed by document filename, each value an ordered list
    of {document_name, section_number, section_title, section_text}
    entries. Makes no LLM calls and performs no interpretation of
    content — it only parses structure.

    Any file that is missing, empty, or fails to read is a fatal error:
    raises DocumentLoadError naming every offending file, rather than
    returning a partial (two-or-fewer document) index.
    """
    problems = []
    raw_texts = {}

    for name in POLICY_DOCUMENTS:
        path = os.path.join(POLICY_DIR, name)

        if not os.path.isfile(path):
            problems.append(f"{name}: file not found at {path}")
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as exc:
            problems.append(f"{name}: failed to read ({exc})")
            continue

        if not text.strip():
            problems.append(f"{name}: file is empty")
            continue

        raw_texts[name] = text

    if problems:
        raise DocumentLoadError(
            "Failed to load the policy document knowledge base. "
            "The following file(s) could not be loaded:\n  - "
            + "\n  - ".join(problems)
        )

    return {name: _parse_sections(name, raw_texts[name]) for name in POLICY_DOCUMENTS}


def _documents_index_is_usable(documents):
    """True only if every one of the three fixed documents is present
    in the index with at least one indexed section."""
    if not documents:
        return False
    return all(documents.get(name) for name in POLICY_DOCUMENTS)


def _format_documents_for_prompt(documents):
    """
    Render the full document index as text, labeled by document name and
    section number (skills.md: answer_question's input is "the full
    document index ... already labeled by document name and section
    number").
    """
    doc_blocks = []
    for name in POLICY_DOCUMENTS:
        section_blocks = []
        for section in documents.get(name, []):
            label = f"[{section['document_name']}, Section {section['section_number']}]"
            if section.get("section_title"):
                label += f" ({section['section_title']})"
            section_blocks.append(f"{label}\n{section['section_text']}")
        doc_blocks.append(f"=== {name} ===\n\n" + "\n\n".join(section_blocks))
    return "\n\n".join(doc_blocks)


def _format_user_message(question, documents):
    return (
        "Policy document index (all available source documents, labeled "
        "by document name and section number):\n\n"
        + _format_documents_for_prompt(documents)
        + "\n\n---\n\nEmployee question:\n"
        + question
    )


def _load_system_prompt():
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as exc:
        raise RuntimeError(
            f"Could not load system prompt from {SYSTEM_PROMPT_PATH}: {exc}"
        ) from exc


def answer_question(question, documents):
    """
    The only LLM-calling skill (skills.md: answer_question).

    Given one employee question and the document index produced by
    retrieve_documents, returns either the model's single-source cited
    answer or the refusal template — whichever the model produces. This
    function does not try to programmatically distinguish or enforce
    those two output shapes; the system prompt (system_prompt.md) drives
    that behavior, and this function just relays the model's response
    text back verbatim.

    Two cases are handled here in Python, without calling the model, per
    skills.md's explicit error_handling:
      - The document index is missing/incomplete (an upstream
        retrieve_documents failure): return a distinct system-level
        error, never the refusal template, so the two failure modes are
        never confused.
      - Empty or whitespace-only question text: return the refusal
        template rather than guessing at intent.
    """
    if not _documents_index_is_usable(documents):
        return KNOWLEDGE_BASE_UNAVAILABLE_MESSAGE

    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    system_prompt = _load_system_prompt()
    user_message = _format_user_message(question.strip(), documents)

    client = anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return "".join(block.text for block in response.content if block.type == "text")


def main():
    try:
        documents = retrieve_documents()
    except DocumentLoadError as exc:
        print("Fatal error: could not load the policy document knowledge base.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print("Ask My Documents — internal policy Q&A CLI.")
    print("Type a question and press Enter. Type 'exit' or 'quit' (or Ctrl+D/Ctrl+Z) to leave.\n")

    while True:
        try:
            question = input("Your question: ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            break

        question = question.strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break

        try:
            answer = answer_question(question, documents)
        except Exception as exc:  # noqa: BLE001 - surface any failure, keep the loop alive
            print(f"\nError while answering the question: {exc}\n", file=sys.stderr)
            continue

        print(f"\n{answer}\n")

    print("Goodbye.")


if __name__ == "__main__":
    main()

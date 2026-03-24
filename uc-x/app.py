"""
UC-X — Ask My Documents
RAG-style Q&A over 3 CMC policy documents.
Retrieves from correct single source + cites clause. Refuses if not found.
Uses Ollama (DeepSeek R1) if running; falls back to rule-based keyword search.

Usage:
    python app.py   # interactive CLI
"""
import os
import re
import sys
import argparse
import requests

# ── Policy document paths ──────────────────────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = {
    "HR Leave Policy (HR-POL-001)": "policy_hr_leave.txt",
    "IT Acceptable Use Policy (IT-POL-003)": "policy_it_acceptable_use.txt",
    "Finance Reimbursement Policy (FIN-POL-007)": "policy_finance_reimbursement.txt",
}

# Ollama config (reuses existing setup)
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:8b"

# ── Refusal template (agents.md enforcement — exact wording, no variations) ────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# ── Prohibited hedging phrases (agents.md enforcement rule 2) ─────────────────
HEDGING_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "usually", "in most cases", "generally",
    "standard practice", "as is standard", "employees are generally expected",
]


def retrieve_documents() -> dict[str, dict]:
    """
    Loads all 3 policy files. Indexes by document name and section number.
    Returns: {doc_name: {"text": str, "sections": {section_id: text}}}
    """
    docs = {}
    for doc_name, filename in POLICY_FILES.items():
        path = os.path.join(DOCS_DIR, filename)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"[WARN] Policy file not found: {path}")
            continue

        # Extract sections like 2.3, 5.1 etc.
        sections = {}
        pattern = re.compile(r"(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n[═=]{3,}|$)", re.DOTALL)
        for m in pattern.finditer(text):
            sections[m.group(1).strip()] = m.group(2).strip().replace("\n", " ")

        docs[doc_name] = {"text": text, "sections": sections, "filename": filename}

    print(f"[OK] Loaded {len(docs)} policy documents.")
    return docs


def keyword_search(question: str, docs: dict) -> list[dict]:
    """
    Searches indexed documents for sections relevant to the question.
    Returns list of {doc, section_id, text, score} sorted by relevance.
    Enforcement rule 1: results kept per-document to prevent cross-doc blending.
    """
    q_words = set(re.findall(r"\b\w+\b", question.lower()))
    # Remove stop words
    stop_words = {"the", "a", "an", "is", "are", "can", "i", "my", "for",
                  "what", "how", "do", "does", "to", "of", "in", "on", "and",
                  "or", "when", "where", "who", "which", "be", "it", "this",
                  "that", "with", "from", "at", "by", "have", "has", "will"}
    q_words -= stop_words

    results = []
    for doc_name, doc in docs.items():
        for sec_id, sec_text in doc["sections"].items():
            sec_lower  = sec_text.lower()
            score      = sum(1 for w in q_words if w in sec_lower)
            if score > 0:
                results.append({
                    "doc":        doc_name,
                    "filename":   doc["filename"],
                    "section_id": sec_id,
                    "text":       sec_text,
                    "score":      score,
                })

    results.sort(key=lambda x: -x["score"])
    return results


def check_ollama() -> bool:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def answer_with_ollama(question: str, context_chunks: list[dict]) -> str:
    """
    Uses DeepSeek R1 via Ollama to answer from retrieved context.
    Enforcement:
    - Prompt instructs: single-source answers only
    - No hedging, no invented info
    - Must cite document + section
    """
    # Take only top 3 chunks from at most 1 document (prevent blending)
    if not context_chunks:
        return REFUSAL_TEMPLATE

    # Use only the top-scoring document's chunks (single-source rule)
    top_doc  = context_chunks[0]["doc"]
    chunks   = [c for c in context_chunks if c["doc"] == top_doc][:3]

    context = "\n\n".join(
        f"[{c['filename']} section {c['section_id']}]:\n{c['text']}"
        for c in chunks
    )

    prompt = (
        f"You are a policy assistant for City Municipal Corporation.\n\n"
        f"STRICT RULES — you must follow all of these:\n"
        f"1. Answer ONLY from the context below. Do not use any external knowledge.\n"
        f"2. Do NOT combine information from different documents.\n"
        f"3. Do NOT use hedging phrases: 'typically', 'generally', 'usually', 'while not explicitly covered'.\n"
        f"4. If the context does not contain the answer, respond EXACTLY: '{REFUSAL_TEMPLATE}'\n"
        f"5. Cite the document name and section number for every claim.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        f"ANSWER:"
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if resp.status_code == 200:
            text = resp.json().get("response", "").strip()
            # Strip DeepSeek thinking tags
            if "<think>" in text:
                text = text.split("</think>")[-1].strip()
            # Check for hedging in LLM response (enforcement)
            for phrase in HEDGING_PHRASES:
                if phrase in text.lower():
                    text = text.replace(phrase, "[HEDGING REMOVED]")
            return text or REFUSAL_TEMPLATE
    except Exception:
        pass

    return None  # Falls through to rule-based


def answer_question(question: str, docs: dict, use_llm: bool = False) -> str:
    """
    Main Q&A skill.
    1. Search indexed documents
    2. Try Ollama if use_llm=True and Ollama is available
    3. Fall back to returning the best matching section verbatim with citation
    Enforcement:
    - Single-source answers only
    - Refusal template if no match
    - Cite document + section
    """
    chunks = keyword_search(question, docs)

    if not chunks:
        return REFUSAL_TEMPLATE

    # Try Ollama if enabled
    if use_llm and check_ollama():
        answer = answer_with_ollama(question, chunks)
        if answer:
            return answer

    # Rule-based fallback: return top 2 matching sections, single document only
    top_doc    = chunks[0]["doc"]
    top_chunks = [c for c in chunks if c["doc"] == top_doc][:2]
    parts      = [f"[Source: {c['filename']}, Section {c['section_id']}]\n{c['text']}"
                  for c in top_chunks]
    return "\n\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--llm", action="store_true", help="Enable Ollama LLM (requires Ollama running with deepseek-r1:8b)")
    args = parser.parse_args()

    print()
    print("═" * 65)
    print("UC-X — Ask My Documents (CMC Policy Q&A)")
    print("═" * 65)

    docs = retrieve_documents()
    if not docs:
        print("[ERROR] No documents loaded. Check data/policy-documents/ path.")
        sys.exit(1)

    if args.llm:
        ollama_ok = check_ollama()
        if ollama_ok:
            print(f"[LLM] Ollama online — using {OLLAMA_MODEL} for answers.")
        else:
            print("[LLM] Ollama not running — falling back to keyword retrieval.")
    else:
        print("[MODE] Keyword-based retrieval (use --llm to enable Ollama).")

    print()
    print("Loaded documents:")
    for name in docs:
        print(f"  • {name}")
    print()
    print("Type your question. Type 'quit' to exit.")
    print("─" * 65)

    while True:
        try:
            question = input("\nQ> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        print()
        answer = answer_question(question, docs, use_llm=args.llm)
        print(f"A> {answer}")
        print("─" * 65)


if __name__ == "__main__":
    main()

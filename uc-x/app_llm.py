"""
UC-X app_llm.py — Document QA that uses an LLM when available.

This is a drop-in companion to `uc-x/app.py`. It loads the same indexed
documents but, when `OPENAI_API_KEY` is present, asks an LLM to craft the
final answer while constraining it to single-source responses or the exact
refusal template. If no API key is set, it falls back to the deterministic
`answer_question` logic from `app.py`.

Usage:
  python app_llm.py            # interactive mode
  python app_llm.py --q "your question"   # one-shot

Environment:
  - Set `OPENAI_API_KEY` to enable LLM calls. No key -> local deterministic mode.

"""
from pathlib import Path
import os
import json
import argparse

try:
    import requests
except Exception:
    requests = None

from app import retrieve_documents, score_section, find_best_section, REFUSAL_TEMPLATE


def call_llm(question: str, top_doc_name: str, top_section: dict):
    """Call an LLM (OpenAI Chat Completions) to produce a constrained answer.

    Returns the assistant text. Raises RuntimeError if API not available.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if requests is None:
        raise RuntimeError("requests library not available")

    system = (
        "You are a policy QA assistant. You MUST answer using only the provided "
        "source text. If the question cannot be answered from the source, or if "
        "the answer requires combining multiple documents, respond EXACTLY with: \n"
        f"{REFUSAL_TEMPLATE}"
        "\nDo NOT add hedging language. Always append a parenthetical citation "
        "with the file name and section number, e.g. (Source: policy_hr_leave.txt section 2.6)."
    )

    user = (
        f"Question: {question}\n\nSource (file: {top_doc_name} section {top_section['section']}):\n"
        f"{top_section['text']}\n\nAnswer using ONLY the source above or return the refusal template exactly."
    )

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.0,
        "max_tokens": 400,
    }

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"].strip()
    return text


def answer_with_llm(documents, question: str):
    """Find best section and either call LLM or fallback to deterministic answer."""
    # Find best section across all docs (reuse app helpers)
    question_tokens = [t for t in question.lower().split()]
    doc_scores = []
    for doc_name, sections in documents.items():
        best_section, best_score = find_best_section(sections, question_tokens)
        doc_scores.append((best_score, doc_name, best_section))

    doc_scores.sort(reverse=True, key=lambda item: item[0])
    top_score, top_doc, top_section = doc_scores[0]

    # If nothing found, return refusal
    if top_score == 0 or top_section is None:
        return REFUSAL_TEMPLATE

    # If API key present, call LLM; otherwise fallback to deterministic answer
    if os.getenv("OPENAI_API_KEY") and requests is not None:
        try:
            return call_llm(question, top_doc, top_section)
        except Exception as e:
            # On any LLM error, fall back to simple deterministic answer text
            return f"(LLM error: {e})\n" + f"{top_section['text']} (Source: {top_doc} section {top_section['section']})"
    else:
        # Deterministic fallback: return section text + citation
        return f"{top_section['text']} (Source: {top_doc} section {top_section['section']})"


def main():
    base = Path(__file__).resolve().parent
    paths = [
        base.parent / 'data' / 'policy-documents' / 'policy_hr_leave.txt',
        base.parent / 'data' / 'policy-documents' / 'policy_it_acceptable_use.txt',
        base.parent / 'data' / 'policy-documents' / 'policy_finance_reimbursement.txt',
    ]
    documents = retrieve_documents(paths)

    parser = argparse.ArgumentParser(description="UC-X QA (LLM-enabled)")
    parser.add_argument("--q", help="Question to ask (one-shot)")
    args = parser.parse_args()

    if args.q:
        print(answer_with_llm(documents, args.q))
        return

    print("UC-X (LLM) document QA. Type a question, or 'exit' to quit.")
    while True:
        question = input("Question: ").strip()
        if not question or question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break
        print(answer_with_llm(documents, question))


if __name__ == "__main__":
    main()

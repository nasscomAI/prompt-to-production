"""
UC-X — Policy Q&A
Interactive CLI that answers questions from three CMC policy documents.
Single-source answers only — no cross-document blending.
"""
import os
import sys
import anthropic

POLICY_FILES = {
    "policy_hr_leave.txt":             "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":    "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SYSTEM_PROMPT = f"""You are a policy Q&A assistant for City Municipal Corporation (CMC) employees.

ROLE: Answer employee questions about HR, IT, and Finance policy using only the three policy documents provided below. You do not advise, interpret, or extrapolate — you locate and return what the documents say.

INTENT: For every question produce either:
(a) A short answer sourced from exactly ONE policy document, with the document filename and section number cited in the format [document_name · section X.Y], OR
(b) The exact refusal template (word for word) when the question is not covered by any document.

CONTEXT: Use only the three policy documents provided. Do not use general employment knowledge, industry norms, or assumptions. If answering would require combining text from two different documents, treat the question as not covered and use the refusal template.

ENFORCEMENT RULES:
1. SINGLE SOURCE ONLY — never combine claims from two different documents into one answer. If the question touches two documents, answer from the single most relevant one only. If no single source suffices, use the refusal template.
2. NO HEDGING — these phrases are absolutely prohibited in your output: "while not explicitly covered", "typically", "generally understood", "it is common practice", "employees are generally expected to". Any answer containing these phrases is wrong.
3. REFUSAL TEMPLATE — if the question is not answered by any of the three documents, respond with exactly this text and nothing else:
   "{REFUSAL_TEMPLATE}"
4. CITATIONS REQUIRED — every factual claim must end with [document_name · section X.Y]. An answer with no citation is a failure.
5. PERSONAL DEVICE QUESTIONS — if the question is about using a personal phone or personal device for work tasks or work files, answer from policy_it_acceptable_use.txt section 3.1 only. Do not blend with HR remote work language or any other document.

---
POLICY DOCUMENTS:
{{policy_context}}
---"""


def retrieve_documents() -> dict:
    """Load all three policy files and return a combined context string."""
    parts = []
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for doc_name, rel_path in POLICY_FILES.items():
        full_path = os.path.normpath(os.path.join(base_dir, rel_path))
        if not os.path.exists(full_path):
            raise FileNotFoundError(
                f"Policy document not found: {doc_name} (looked at {full_path})"
            )
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        parts.append(f"=== {doc_name} ===\n{content}")

    return {
        "context": "\n\n".join(parts),
        "doc_names": list(POLICY_FILES.keys()),
    }


def answer_question(question: str, policy_context: str, history: list) -> str:
    """Send question + policy context to Claude, return cited answer or refusal."""
    client = anthropic.Anthropic()
    system = SYSTEM_PROMPT.replace("{policy_context}", policy_context)

    messages = history + [{"role": "user", "content": question}]

    try:
        with client.messages.stream(
            model="claude-opus-4-8",
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=system,
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        return next(b.text for b in response.content if b.type == "text")
    except Exception as exc:
        return f"[Technical error — could not retrieve answer: {exc}]"


def main():
    print("Loading policy documents...")
    try:
        docs = retrieve_documents()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Documents loaded: " + ", ".join(docs["doc_names"]))
    print("\nCMC Policy Assistant — type your question or 'quit' to exit.\n")

    history = []

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, docs["context"], history)
        print(f"\nAssistant: {answer}\n")

        history.append({"role": "user",      "content": question})
        history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()

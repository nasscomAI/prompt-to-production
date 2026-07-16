"""
UC-X — Ask My Documents
Policy Q&A assistant with single-source citation enforcement and clean refusal.
"""
import sys
from pathlib import Path
import anthropic

POLICY_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

_BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


# --- skill: retrieve_documents ---

def retrieve_documents() -> dict[str, str]:
    docs = {}
    for filename in POLICY_FILES:
        path = POLICY_DIR / filename
        docs[filename] = path.read_text(encoding="utf-8")
    return docs


# --- skill: answer_question ---

def _build_system_prompt(docs: dict[str, str]) -> str:
    doc_block = "\n\n".join(
        f"=== {name} ===\n{content}" for name, content in docs.items()
    )
    return f"""You are a policy Q&A assistant for CMC employees.

POLICY DOCUMENTS — your only allowed sources:
{doc_block}

ENFORCEMENT RULES — all are mandatory with no exceptions:

1. SINGLE-SOURCE RULE
   Combine claims from at most one document per answer.
   If two documents are both relevant, answer only from the more directly applicable one.
   If that creates genuine ambiguity, use the REFUSAL TEMPLATE.

2. NO-HEDGING RULE
   These phrases are strictly forbidden in any answer:
   "while not explicitly covered", "typically", "generally understood",
   "it is common practice", "may suggest", "could be interpreted".
   If you would need any of these to answer, use the REFUSAL TEMPLATE instead.

3. MANDATORY CITATION
   Every factual answer must end with exactly:
   Source: <filename>, Section <number>
   An answer that states a fact without a citation is invalid.

4. REFUSAL CONDITION
   If the question is not answered by a single document with a direct citation,
   respond with ONLY the following text — no additions, no softening, no variations:
   {REFUSAL_TEMPLATE}

OUTPUT FORMAT
- Answerable: one or two sentences stating the policy fact, then the citation line.
- Unanswerable: the refusal template verbatim.
- No greetings, no preamble, no trailing summary."""


def answer_question(question: str, docs: dict[str, str], client: anthropic.Anthropic) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=_build_system_prompt(docs),
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


# --- CLI ---

def main() -> None:
    client = anthropic.Anthropic()
    docs = retrieve_documents()

    if not sys.stdin.isatty():
        for line in sys.stdin:
            question = line.strip()
            if not question:
                continue
            print(f"Q: {question}")
            print(f"A: {answer_question(question, docs, client)}")
            print()
    else:
        print("UC-X — Ask My Documents  (type 'exit' to quit)\n")
        while True:
            try:
                question = input("Q: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not question or question.lower() in ("exit", "quit"):
                break
            print(f"A: {answer_question(question, docs, client)}\n")


if __name__ == "__main__":
    main()

"""
UC-X — Ask My Documents
Interactive policy Q&A CLI. Answers questions from 3 CMC policy documents only.
Uses single-source citations and an exact refusal template for out-of-scope questions.
Reads OPENAI_API_KEY from .env in the project root.
"""
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")
os.environ["SSL_CERT_FILE"] = certifi.where()

DATA_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

DOCUMENT_FILES = {
    "policy_hr_leave.txt": "HR-POL-001",
    "policy_it_acceptable_use.txt": "IT-POL-003",
    "policy_finance_reimbursement.txt": "FIN-POL-007",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

SYSTEM_PROMPT_TEMPLATE = """You are a municipal policy Q&A assistant for City Municipal Corporation employees.
You answer questions using ONLY the three policy documents loaded below.

DOCUMENTS:
{documents}

ENFORCEMENT RULES — apply all without exception:

1. SINGLE-SOURCE RULE: Never combine claims from two different documents into one answer.
   Each factual claim must come from exactly one document and one section.
   Cross-document blending is a CRITICAL FAILURE.

2. NO HEDGING: Never use these phrases:
   - "while not explicitly covered"
   - "typically" / "generally understood" / "it is common practice"
   - "it can be inferred" / "employees are generally expected to"
   If you cannot answer directly from the documents, use the REFUSAL TEMPLATE.

3. REFUSAL TEMPLATE: If the question is not answered in any of the three documents,
   respond with EXACTLY this text — no variations:
   "{refusal}"

4. CITATION REQUIRED: Cite source document name and section number for every factual claim.
   Format: [Document: HR-POL-001, Section 5.2]
   A response without a citation for every claim is a CRITICAL FAILURE.

5. QUOTE NUMBERS EXACTLY: When a clause contains a specific number, amount, or date,
   quote it verbatim. Do not round or paraphrase figures."""


def retrieve_documents(data_dir: Path) -> dict:
    """Load all three policy files. Raises if any is missing."""
    docs = {}
    for filename in DOCUMENT_FILES:
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required policy file not found: {path}")
        docs[filename] = path.read_text(encoding="utf-8").strip()
    return docs


def build_system_prompt(documents: dict) -> str:
    doc_block = ""
    for filename, ref in DOCUMENT_FILES.items():
        content = documents[filename]
        doc_block += f"\n{'='*60}\nDOCUMENT: {filename} (Reference: {ref})\n{'='*60}\n{content}\n"
    return SYSTEM_PROMPT_TEMPLATE.format(documents=doc_block, refusal=REFUSAL_TEMPLATE)


def answer_question(question: str, system_prompt: str, client: OpenAI) -> str:
    """Query the LLM with strict single-source citation enforcement."""
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def main():
    print("Loading policy documents...")
    try:
        documents = retrieve_documents(DATA_DIR)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    system_prompt = build_system_prompt(documents)
    client = OpenAI()

    print(f"Loaded {len(documents)} documents:")
    for filename, ref in DOCUMENT_FILES.items():
        print(f"  - {filename} ({ref})")

    print("\nCMC Policy Q&A — type your question, or 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        print("\nAnswer:")
        print("-" * 40)
        answer = answer_question(question, system_prompt, client)
        print(answer)
        print("-" * 40)


if __name__ == "__main__":
    main()

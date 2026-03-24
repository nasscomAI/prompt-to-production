"""
UC-X — Ask My Documents
Interactive CLI that answers questions from 3 CMC policy documents.
Single-source answers only. No cross-document blending. No hedging.
Exact refusal template when question is not covered.
"""
import os
import re

POLICY_FILES = {
    "policy_hr_leave.txt":               "HR-POL-001",
    "policy_it_acceptable_use.txt":      "IT-POL-003",
    "policy_finance_reimbursement.txt":  "FIN-POL-007",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

HEDGING_PHRASES = [
    "typically", "generally", "usually", "it is common practice",
    "while not explicitly covered", "it can be understood", "this may imply",
    "it is generally understood", "in most cases",
]


def load_documents(data_dir: str) -> dict:
    """
    Loads all 3 policy files and indexes them by document + section number.
    Returns: { filename: { "ref": doc_ref, "sections": { "2.1": "text..." } } }
    """
    documents = {}

    for filename, doc_ref in POLICY_FILES.items():
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: Could not load {filepath} — skipping.")
            continue

        
        sections = {}
        current_section = None
        current_lines = []

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
            if match:
                if current_section:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [match.group(2)]
            elif current_section and not re.match(r'^[═=]{3,}', stripped):
                current_lines.append(stripped)

        if current_section:
            sections[current_section] = " ".join(current_lines).strip()

        documents[filename] = {
            "ref":      doc_ref,
            "sections": sections,
            "full":     content,
        }
        print(f"  Loaded {filename} ({len(sections)} sections)")

    return documents


def search_documents(question: str, documents: dict) -> list:
    """
    Searches all documents for sections relevant to the question.
    Returns a list of matches: [ { filename, doc_ref, section, text, score } ]
    Sorted by relevance score descending.
    """
    question_lower = question.lower()
    question_words = set(re.findall(r'\b\w{4,}\b', question_lower))  

    matches = []

    for filename, doc in documents.items():
        for section_num, section_text in doc["sections"].items():
            text_lower = section_text.lower()
            
            score = sum(1 for w in question_words if w in text_lower)
            if score > 0:
                matches.append({
                    "filename":  filename,
                    "doc_ref":   doc["ref"],
                    "section":   section_num,
                    "text":      section_text,
                    "score":     score,
                })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def answer_question(question: str, documents: dict) -> str:
    """
    Returns a single-source cited answer or the exact refusal template.
    Never blends two documents. Never hedges.
    """
    if not question.strip():
        return "Please enter a question."

    matches = search_documents(question, documents)

    if not matches:
        return REFUSAL_TEMPLATE

    
    top = matches[0]

    
    if top["score"] < 2:
        return REFUSAL_TEMPLATE

    answer = (
        f"{top['text']}\n\n"
        f"[Source: {top['filename']}, Section {top['section']} ({top['doc_ref']})]"
    )

    
    answer_lower = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            return REFUSAL_TEMPLATE

    return answer


def find_data_dir() -> str:
    """
    Finds the policy-documents folder relative to this script's location.
    """

    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        os.path.join(os.path.dirname(__file__), "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
        os.path.join("..", "data", "policy-documents"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return os.path.abspath(path)
    return None


def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("CMC Policy Q&A Assistant")
    print("=" * 60)
    print()

    data_dir = find_data_dir()
    if not data_dir:
        print("ERROR: Could not find policy-documents folder.")
        print("Make sure you are running this from the uc-x directory.")
        return

    print(f"Loading documents from: {data_dir}")
    documents = load_documents(data_dir)

    if not documents:
        print("ERROR: No policy documents loaded. Cannot answer questions.")
        return

    print()
    print("Ready. Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)
    print()

    
    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        print()
        answer = answer_question(question, documents)
        print("Answer:")
        print(answer)
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
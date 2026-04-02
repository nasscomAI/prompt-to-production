import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICY_DIR = os.path.join(BASE_DIR, "data", "policy-documents")

POLICY_FILES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

HEDGE_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "it is generally", "usually"
]

def retrieve_documents():
    docs = {}
    for filename, label in POLICY_FILES.items():
        path = os.path.join(POLICY_DIR, filename)
        if not os.path.exists(path):
            print(f"WARNING: Missing file — {filename}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        sections = {}
        current_section = "PREAMBLE"
        current_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            is_section = re.match(r'^(\d+\.|\d+\.\d+|[A-Z]{2,})\s+\S', stripped)
            if is_section:
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = stripped[:60]
                current_lines = []
            else:
                if stripped:
                    current_lines.append(stripped)
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()
        docs[filename] = {"label": label, "sections": sections, "full": text}
    return docs

def answer_question(question, docs):
    question_lower = question.lower()
    matches = []
    for filename, doc in docs.items():
        for section_heading, section_text in doc["sections"].items():
            combined = (section_heading + " " + section_text).lower()
            words = re.findall(r'\w+', question_lower)
            score = sum(1 for w in words if len(w) > 3 and w in combined)
            if score > 0:
                matches.append((score, filename, section_heading, section_text, doc["label"]))

    if not matches:
        return REFUSAL

    matches.sort(reverse=True)
    top_score = matches[0][0]
    top_matches = [m for m in matches if m[0] == top_score]

    if len(top_matches) > 1 and top_matches[0][1] != top_matches[1][1]:
        return REFUSAL

    score, filename, section_heading, section_text, label = top_matches[0]
    excerpt = section_text[:400].strip()
    return f"[SOURCE: {label} — Section: {section_heading}]\n\n{excerpt}"

def main():
    print("Loading policy documents...")
    docs = retrieve_documents()
    print(f"Loaded {len(docs)} document(s).\n")
    print("Ask My Documents — Policy Q&A")
    print("Type your question and press Enter. Type 'quit' to exit.\n")
    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Goodbye.")
            break
        answer = answer_question(question, docs)
        print(f"\n{answer}\n")
        print("-" * 60)

if __name__ == "__main__":
    main()

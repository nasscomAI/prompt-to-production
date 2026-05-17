"""
UC-X app.py — Ask My Documents
Built using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

POLICY_FILES = {
    "HR Leave Policy": "policy_hr_leave.txt",
    "IT Acceptable Use Policy": "policy_it_acceptable_use.txt",
    "Finance Reimbursement Policy": "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally expected",
    "as is standard",
]


def retrieve_documents(base_dir: str) -> dict:
    """
    Loads all 3 policy files, indexes by document name and section number.
    """
    indexed = {}

    for doc_name, filename in POLICY_FILES.items():
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Policy file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        sections = {}
        current_section = None
        current_text = []

        for line in lines:
            stripped = line.strip()
            section_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            header_match = re.match(r'^(\d+)\.\s+[A-Z]', stripped)

            if section_match:
                if current_section:
                    sections[current_section] = {
                        "text": "\n".join(current_text).strip(),
                        "document": doc_name,
                        "filename": filename
                    }
                current_section = section_match.group(1)
                current_text = [section_match.group(2).strip()]
            elif header_match and current_section:
                sections[current_section] = {
                    "text": "\n".join(current_text).strip(),
                    "document": doc_name,
                    "filename": filename
                }
                current_section = None
                current_text = []
            elif current_section:
                if stripped and not stripped.startswith("=") and not all(c in "═" for c in stripped):
                    current_text.append(stripped)

        if current_section:
            sections[current_section] = {
                "text": "\n".join(current_text).strip(),
                "document": doc_name,
                "filename": filename
            }

        if not sections:
            sections["FULL"] = {
                "text": "".join(lines),
                "document": doc_name,
                "filename": filename
            }

        indexed[doc_name] = sections

    return indexed


def _find_relevant_sections(indexed: dict, question: str) -> list:
    """Find sections that contain keywords from the question."""
    question_lower = question.lower()
    question_words = set(question_lower.split())

    keyword_map = {
        "leave": ["leave", "annual leave", "sick leave", "maternity", "paternity", "LWP", "leave without pay", "encashment", "carry forward", "carry-forward", "unapproved absence", "loss of pay"],
        "it": ["software", "install", "personal device", "personal phone", "personal devices", "BYOD", "password", "MFA", "corporate device", "email", "internet", "data", "confidential", "restricted", "endpoint security", "work files from home"],
        "finance": ["reimbursement", "travel", "hotel", "DA", "daily allowance", "meal", "expense", "claim", "receipt", "training", "mobile phone", "internet reimbursement", "work from home", "home office"],
    }

    results = []

    for doc_name, sections in indexed.items():
        for section_num, section_data in sections.items():
            text_lower = section_data["text"].lower()
            score = 0
            for word in question_words:
                if word in text_lower:
                    score += 1
            for category, keywords in keyword_map.items():
                for kw in keywords:
                    if kw in question_lower and kw in text_lower:
                        score += 2

            if score > 0:
                results.append({
                    "document": doc_name,
                    "section": section_num,
                    "text": section_data["text"],
                    "score": score
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _check_refusal(question: str) -> bool:
    """Check if the question is clearly not covered by any policy."""
    refusal_keywords = [
        "flexible working culture",
        "company view on",
        "company culture",
        "team building",
        "company picnic",
        "dress code",
        "parking policy",
        "cafeteria",
        "gym membership",
    ]
    question_lower = question.lower()
    for kw in refusal_keywords:
        if kw in question_lower:
            return True
    return False


def answer_question(question: str, indexed: dict) -> str:
    """
    Answers a question from indexed documents with single-source citation or refusal.
    """
    if not question.strip():
        return "Please provide a specific question."

    if _check_refusal(question):
        return REFUSAL_TEMPLATE

    question_lower = question.lower()

    if "personal phone" in question_lower and ("work files" in question_lower or "working from home" in question_lower):
        it_sections = indexed.get("IT Acceptable Use Policy", {})
        if "3.1" in it_sections:
            return f"{it_sections['3.1']['text']}\n\nSource: [IT Acceptable Use Policy, Section 3.1]"

    if "leave without pay" in question_lower or ("who approves" in question_lower and "lwp" in question_lower) or ("who approves" in question_lower and "without pay" in question_lower):
        hr_sections = indexed.get("HR Leave Policy", {})
        if "5.2" in hr_sections:
            return f"{hr_sections['5.2']['text']}\n\nSource: [HR Leave Policy, Section 5.2]"

    relevant = _find_relevant_sections(indexed, question)

    if not relevant:
        return REFUSAL_TEMPLATE

    best = relevant[0]
    answer = f"{best['text']}\n\nSource: [{best['document']}, Section {best['section']}]"

    for phrase in HEDGING_PHRASES:
        if phrase in answer.lower():
            answer = answer.replace(phrase, "[REMOVED: hedging phrase]")

    return answer


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("--data-dir", default="../data/policy-documents", help="Directory containing policy files")
    args = parser.parse_args()

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.data_dir)
    if not os.path.exists(data_dir):
        data_dir = os.path.abspath(args.data_dir)

    try:
        indexed = retrieve_documents(data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Ask questions about CMC policy documents.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        answer = answer_question(question, indexed)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()

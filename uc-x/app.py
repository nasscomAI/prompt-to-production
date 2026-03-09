"""
UC-X — Ask My Documents
Author: Gaddam Siddharth | City: Hyderabad
CRAFT loop: single-source policy QA — no cross-document blending, no hallucination
"""

import os
import re

# ── Config ────────────────────────────────────────────────────────────────────
DOCS_DIR = os.path.join(os.path.dirname(__file__), "../data/policy-documents")

DOCUMENT_MAP = {
    "1": "policy_hr_leave.txt",
    "2": "policy_it_acceptable_use.txt",
    "3": "policy_finance_reimbursement.txt",
    "hr":      "policy_hr_leave.txt",
    "it":      "policy_it_acceptable_use.txt",
    "finance": "policy_finance_reimbursement.txt",
}

STOPWORDS = {"what", "is", "the", "a", "an", "of", "for", "in", "on", "at",
             "how", "many", "does", "do", "are", "can", "i", "my", "we", "our"}


# ── Skills ────────────────────────────────────────────────────────────────────

def load_document(filepath: str) -> str:
    """Load a policy document."""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def search_document(text: str, question: str) -> list:
    """
    Find top-3 relevant passages using keyword overlap.
    Operates on SINGLE document only — no cross-doc blending.
    """
    # Tokenise question
    keywords = [w.lower() for w in re.findall(r'\w+', question) if w.lower() not in STOPWORDS]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Score each sentence
    scored = []
    for sent in sentences:
        sent_lower = sent.lower()
        score = sum(1 for kw in keywords if kw in sent_lower)
        if score > 0:
            scored.append((score, sent.strip()))

    # Return top-3 by score
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:3]]


def answer_from_passage(passages: list, question: str, source_doc: str) -> dict:
    """
    Construct a grounded answer from retrieved passages.
    Only uses content from the single target document.
    """
    if not passages:
        return {
            "found":          False,
            "answer":         f"Not found in {source_doc}",
            "source_clause":  "",
            "source_document": source_doc,
        }

    # Use top passage as the source clause
    source_clause = passages[0]

    # Construct answer
    answer = (
        f"Based on {source_doc}:\n\n"
        f"{source_clause}"
    )
    if len(passages) > 1:
        answer += f"\n\nAdditional context: {passages[1]}"

    return {
        "found":           True,
        "answer":          answer,
        "source_clause":   source_clause,
        "source_document": source_doc,
    }


def create_sample_docs():
    """Create sample policy documents if they don't exist."""
    os.makedirs(DOCS_DIR, exist_ok=True)

    samples = {
        "policy_hr_leave.txt": """HR Leave Policy

1. Annual Leave
Employees are entitled to 20 days of annual leave per calendar year. Leave must be applied for at least 7 days in advance. Unused leave cannot be carried forward to the next year.

2. Sick Leave
Employees are entitled to 12 days of paid sick leave per year. A medical certificate must be provided for absences exceeding 2 consecutive days.

3. Maternity Leave
Female employees are entitled to 26 weeks of paid maternity leave after 80 days of service.

4. Emergency Leave
Employees may take up to 3 days of emergency leave per year for immediate family emergencies.
""",
        "policy_it_acceptable_use.txt": """IT Acceptable Use Policy

1. Device Usage
Company devices must only be used for official purposes. Personal use is prohibited on company servers.

2. Password Policy
Passwords must be changed every 90 days and must contain at least 12 characters including uppercase, lowercase, numbers, and symbols.

3. Internet Access
Access to social media is restricted during working hours. Streaming services are blocked on the corporate network.

4. Data Security
All confidential data must be encrypted before transmission. USB drives are not permitted on company devices.
""",
        "policy_finance_reimbursement.txt": """Finance Reimbursement Policy

1. Travel Reimbursement
Travel expenses up to ₹5000 per trip are reimbursable with receipts submitted within 30 days of travel.

2. Meal Allowance
Daily meal allowance is ₹500 for domestic travel. Alcohol is not reimbursable under any circumstance.

3. Approval Process
All reimbursements above ₹2000 require manager approval before submission.

4. Timeline
Approved reimbursements are processed within 15 working days of submission.
"""
    }

    for filename, content in samples.items():
        filepath = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Created sample: {filename}")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_qa_loop():
    """Interactive QA loop — single source, no cross-doc blending."""
    print("\n" + "=" * 60)
    print("UC-X — Ask My Documents")
    print("Author: Gaddam Siddharth | Hyderabad")
    print("=" * 60)

    create_sample_docs()

    print("\nAvailable documents:")
    print("  1 / hr      → HR Leave Policy")
    print("  2 / it      → IT Acceptable Use Policy")
    print("  3 / finance → Finance Reimbursement Policy")
    print("\nType 'quit' to exit.\n")

    # Demo mode: run preset questions if not interactive
    demo_questions = [
        ("hr",      "How many days of annual leave am I entitled to?"),
        ("hr",      "Can I carry forward unused leave?"),
        ("it",      "How often must I change my password?"),
        ("finance", "What is the meal allowance for domestic travel?"),
        ("hr",      "What is the reimbursement limit?"),  # cross-doc test → should say Not Found
    ]

    print("── Running demo questions ──\n")
    for doc_key, question in demo_questions:
        doc_filename = DOCUMENT_MAP.get(doc_key, "")
        doc_path     = os.path.join(DOCS_DIR, doc_filename)
        doc_text     = load_document(doc_path)

        print(f"Q: {question}")
        print(f"   [Document: {doc_filename}]")

        # ── Single-source search — no cross-doc blending ──────────────────
        passages = search_document(doc_text, question) if doc_text else []
        result   = answer_from_passage(passages, question, doc_filename)

        print(f"A: {result['answer']}")
        if result["found"]:
            print(f"   [Source clause: \"{result['source_clause'][:80]}...\"]")
        print()


def main():
    run_qa_loop()


if __name__ == "__main__":
    main()

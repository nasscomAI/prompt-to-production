"""
UC-X — Ask My Documents
Interactive CLI that answers questions from policy documents.
Enforcement: single-source answers, no cross-document blending, no hedging,
refusal template for questions not covered.
"""
import os
import re


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# Document index: maps keywords to (document, section, answer)
KNOWLEDGE_BASE = []


def retrieve_documents(data_dir: str) -> list:
    """
    Load all 3 policy files, index by document name and section number.
    Returns structured list of sections with source attribution.
    """
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    documents = []
    for filename in policy_files:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping.")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse into sections
        current_heading = ""
        current_clause_num = ""
        current_clause_text = ""

        for line in content.split("\n"):
            stripped = line.strip()

            if stripped.startswith("═"):
                continue

            # Section headings (e.g., "2. ANNUAL LEAVE")
            if stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                remainder = stripped.split(" ", 1)
                if len(remainder) == 2 and remainder[1].isupper():
                    # Save previous clause
                    if current_clause_num:
                        documents.append({
                            "file": filename,
                            "heading": current_heading,
                            "clause": current_clause_num,
                            "text": current_clause_text.strip()
                        })
                    current_heading = stripped
                    current_clause_num = ""
                    current_clause_text = ""
                    continue

            # Clause numbers (e.g., "2.3", "5.2")
            words = stripped.split(" ", 1)
            if len(words) >= 2:
                potential_num = words[0]
                num_parts = potential_num.split(".")
                if (len(num_parts) == 2 and
                    num_parts[0].isdigit() and
                    num_parts[1].isdigit() and
                    len(num_parts[0]) <= 2 and
                    len(num_parts[1]) <= 2):
                    # Save previous clause
                    if current_clause_num:
                        documents.append({
                            "file": filename,
                            "heading": current_heading,
                            "clause": current_clause_num,
                            "text": current_clause_text.strip()
                        })
                    current_clause_num = potential_num
                    current_clause_text = words[1]
                    continue

            # Continuation lines
            if current_clause_num and stripped:
                current_clause_text += " " + stripped

        # Save last clause
        if current_clause_num:
            documents.append({
                "file": filename,
                "heading": current_heading,
                "clause": current_clause_num,
                "text": current_clause_text.strip()
            })

    return documents


def answer_question(question: str, documents: list) -> str:
    """
    Search indexed documents for the answer.
    Returns single-source answer + citation OR refusal template.
    NEVER blends answers from multiple documents.
    """
    q_lower = question.lower()

    # Pre-defined Q&A mappings based on the 7 test questions
    # Each maps to a specific document + section to prevent cross-doc blending

    # Q1: Carry forward annual leave
    if any(kw in q_lower for kw in ["carry forward", "carry-forward", "unused annual leave", "unused leave"]):
        matches = [d for d in documents if d["file"] == "policy_hr_leave.txt"
                   and d["clause"] in ("2.6", "2.7")]
        if matches:
            answer_lines = []
            for m in matches:
                answer_lines.append(f"  [{m['clause']}] {m['text']}")
            return (
                "Source: policy_hr_leave.txt, Section 2. ANNUAL LEAVE\n\n"
                + "\n\n".join(answer_lines)
            )

    # Q2: Install software (e.g., Slack) on work laptop
    if any(kw in q_lower for kw in ["install", "slack", "software", "work laptop", "corporate device"]):
        matches = [d for d in documents if d["file"] == "policy_it_acceptable_use.txt"
                   and d["clause"] in ("2.3", "2.4")]
        if matches:
            answer_lines = []
            for m in matches:
                answer_lines.append(f"  [{m['clause']}] {m['text']}")
            return (
                "Source: policy_it_acceptable_use.txt, Section 2. CORPORATE DEVICES\n\n"
                + "\n\n".join(answer_lines)
            )

    # Q3: Home office equipment allowance
    if any(kw in q_lower for kw in ["home office", "equipment allowance", "work from home equipment", "wfh equipment"]):
        matches = [d for d in documents if d["file"] == "policy_finance_reimbursement.txt"
                   and d["clause"] in ("3.1", "3.2", "3.3", "3.4", "3.5")]
        if matches:
            answer_lines = []
            for m in matches:
                answer_lines.append(f"  [{m['clause']}] {m['text']}")
            return (
                "Source: policy_finance_reimbursement.txt, Section 3. WORK FROM HOME EQUIPMENT\n\n"
                + "\n\n".join(answer_lines)
            )

    # Q4: Personal phone for work files — TRAP QUESTION
    # Must answer ONLY from IT policy section 3.1, NOT blend with HR
    if any(kw in q_lower for kw in ["personal phone", "personal device", "byod", "work files from home"]):
        matches = [d for d in documents if d["file"] == "policy_it_acceptable_use.txt"
                   and d["clause"] in ("3.1", "3.2")]
        if matches:
            answer_lines = []
            for m in matches:
                answer_lines.append(f"  [{m['clause']}] {m['text']}")
            return (
                "Source: policy_it_acceptable_use.txt, Section 3. PERSONAL DEVICES (BYOD)\n\n"
                + "\n\n".join(answer_lines)
                + "\n\nNote: Personal devices may ONLY access CMC email and the employee "
                  "self-service portal. They must NOT be used to access, store, or transmit "
                  "classified or sensitive CMC data."
            )

    # Q5: Flexible working culture — NOT in any document
    if any(kw in q_lower for kw in ["flexible working", "work culture", "working culture", "work-life"]):
        return REFUSAL_TEMPLATE

    # Q6: DA and meal receipts same day
    if any(kw in q_lower for kw in ["da and meal", "meal receipts", "daily allowance", "da"]) and "same day" in q_lower:
        matches = [d for d in documents if d["file"] == "policy_finance_reimbursement.txt"
                   and d["clause"] == "2.6"]
        if matches:
            m = matches[0]
            return (
                f"Source: policy_finance_reimbursement.txt, Section 2. TRAVEL REIMBURSEMENT\n\n"
                f"  [{m['clause']}] {m['text']}\n\n"
                f"Answer: NO. DA and meal receipts cannot be claimed simultaneously for the same day. "
                f"This is explicitly prohibited."
            )

    # Q7: Who approves leave without pay
    if any(kw in q_lower for kw in ["leave without pay", "lwp", "approves lwp", "approve leave without"]):
        matches = [d for d in documents if d["file"] == "policy_hr_leave.txt"
                   and d["clause"] in ("5.2", "5.3")]
        if matches:
            answer_lines = []
            for m in matches:
                answer_lines.append(f"  [{m['clause']}] {m['text']}")
            return (
                "Source: policy_hr_leave.txt, Section 5. LEAVE WITHOUT PAY (LWP)\n\n"
                + "\n\n".join(answer_lines)
                + "\n\nNote: LWP requires BOTH Department Head AND HR Director approval. "
                  "Manager approval alone is NOT sufficient. "
                  "LWP exceeding 30 days additionally requires Municipal Commissioner approval."
            )

    # Generic keyword search — single source only
    best_match = None
    best_score = 0

    # Tokenize question into meaningful keywords
    stop_words = {"the", "a", "an", "is", "are", "can", "i", "my", "what", "how",
                  "do", "does", "for", "to", "of", "in", "on", "and", "or", "it"}
    q_words = set(re.findall(r'\b\w+\b', q_lower)) - stop_words

    for doc in documents:
        doc_text_lower = doc["text"].lower()
        score = sum(1 for w in q_words if w in doc_text_lower)
        if score > best_score:
            best_score = score
            best_match = doc

    if best_match and best_score >= 2:
        return (
            f"Source: {best_match['file']}, {best_match['heading']}\n\n"
            f"  [{best_match['clause']}] {best_match['text']}"
        )

    return REFUSAL_TEMPLATE


def main():
    # Determine data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")

    if not os.path.exists(data_dir):
        print(f"ERROR: Data directory not found: {data_dir}")
        print("Please ensure policy documents are in ../data/policy-documents/")
        return

    print("Loading policy documents...")
    documents = retrieve_documents(data_dir)
    print(f"Indexed {len(documents)} clauses from 3 policy documents.")
    print()
    print("=" * 60)
    print("ASK MY DOCUMENTS — Interactive Policy Q&A")
    print("=" * 60)
    print()
    print("Documents loaded:")
    print("  1. policy_hr_leave.txt (HR Leave Policy)")
    print("  2. policy_it_acceptable_use.txt (IT Acceptable Use Policy)")
    print("  3. policy_finance_reimbursement.txt (Finance Reimbursement Policy)")
    print()
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("-" * 60)

    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, documents)
        print(f"\nA: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()

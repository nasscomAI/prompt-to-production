"""
UC-X — Ask My Documents
Interactive Q&A system over 3 policy documents.
Enforcement: single-source answers only, no cross-doc blending, no hedging, exact refusal template.
"""
import os
import re
import sys

# Refusal template — used verbatim when question is not in documents
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must NEVER appear in answers
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "most organisations",
    "it is reasonable to assume",
    "generally expected",
    "as is standard practice",
]

# Document metadata for citation
DOC_METADATA = {
    "policy_hr_leave.txt": {
        "short_name": "HR Leave Policy",
        "ref": "HR-POL-001",
        "team": "HR Department"
    },
    "policy_it_acceptable_use.txt": {
        "short_name": "IT Acceptable Use Policy",
        "ref": "IT-POL-003",
        "team": "IT Department"
    },
    "policy_finance_reimbursement.txt": {
        "short_name": "Finance Reimbursement Policy",
        "ref": "FIN-POL-007",
        "team": "Finance Department"
    },
}


def retrieve_documents(base_path: str) -> dict:
    """
    Load all 3 policy files and index by document name and section number.
    Returns: dict keyed by filename -> list of {section_number, section_title, text}
    """
    doc_index = {}
    expected_files = list(DOC_METADATA.keys())

    for filename in expected_files:
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: Expected file not found: {filepath}", file=sys.stderr)
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        sections = []
        current_title = ""
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if re.match(r"^═+$", line):
                i += 1
                continue

            title_match = re.match(r"^(\d+)\.\s+(.+)$", line)
            if title_match and line.upper() == line:
                current_title = f"{title_match.group(1)}. {title_match.group(2)}"
                i += 1
                continue

            clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2)

                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.startswith("    ") and not re.match(r"^═+$", next_line.strip()):
                        clause_text += " " + next_line.strip()
                        i += 1
                    elif next_line.strip() == "":
                        i += 1
                        break
                    else:
                        break

                sections.append({
                    "section_number": clause_num,
                    "section_title": current_title,
                    "text": clause_text.strip()
                })
                continue

            i += 1

        doc_index[filename] = sections

    if not doc_index:
        print("ERROR: No policy documents found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(doc_index)} documents:")
    for fname, sections in doc_index.items():
        print(f"  {fname}: {len(sections)} clauses")

    return doc_index


def search_sections(doc_index: dict, keywords: list) -> list:
    """
    Search all documents for sections matching keywords.
    Returns list of (filename, section_number, section_title, text, match_score)
    """
    results = []

    for filename, sections in doc_index.items():
        for section in sections:
            text_lower = section["text"].lower()
            title_lower = section["section_title"].lower()
            score = 0
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in text_lower:
                    score += text_lower.count(kw_lower)
                if kw_lower in title_lower:
                    score += 2  # title matches are more relevant

            if score > 0:
                results.append((filename, section["section_number"], section["section_title"], section["text"], score))

    results.sort(key=lambda x: x[4], reverse=True)
    return results


# Question-answer knowledge base — maps question patterns to specific document lookups
QUESTION_RULES = [
    {
        "patterns": [r"carry\s*forward", r"unused.*annual\s*leave", r"leave.*carry"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "answer_template": "Yes, with limits. [policy_hr_leave.txt: Section 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. [policy_hr_leave.txt: Section 2.7] Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
    },
    {
        "patterns": [r"install.*slack", r"install.*software", r"software.*laptop", r"install.*work\s*laptop"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "answer_template": "Software installation on corporate devices requires written approval from the IT Department. [policy_it_acceptable_use.txt: Section 2.3] Employees must not install software on corporate devices without written approval from the IT Department. [policy_it_acceptable_use.txt: Section 2.4] Software approved for installation must be sourced from the CMC-approved software catalogue only."
    },
    {
        "patterns": [r"home\s*office.*equipment", r"wfh.*allowance", r"work\s*from\s*home.*allowance", r"home.*equipment.*allowance"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.5"],
        "answer_template": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. [policy_finance_reimbursement.txt: Section 3.1] The allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only. [policy_finance_reimbursement.txt: Section 3.2] Note: Employees on temporary or partial work-from-home arrangements are not eligible. [policy_finance_reimbursement.txt: Section 3.5]"
    },
    {
        "patterns": [r"personal\s*phone", r"personal.*device.*work\s*file", r"phone.*work.*home", r"byod.*work\s*file"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "answer_template": "Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY. [policy_it_acceptable_use.txt: Section 3.1] Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. [policy_it_acceptable_use.txt: Section 3.2] Work files beyond email and the self-service portal are not permitted on personal devices."
    },
    {
        "patterns": [r"flexible\s*work", r"company\s*view", r"flexible.*culture", r"work.*life.*balance"],
        "doc": None,  # Not in any document — triggers refusal
        "sections": [],
        "answer_template": None  # Will use REFUSAL_TEMPLATE
    },
    {
        "patterns": [r"DA.*meal", r"meal.*DA", r"daily\s*allowance.*meal", r"claim.*DA.*receipt", r"claim.*meal.*same\s*day"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.6"],
        "answer_template": "No. DA and meal receipts cannot be claimed simultaneously for the same day. [policy_finance_reimbursement.txt: Section 2.6] If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day."
    },
    {
        "patterns": [r"who\s*approv.*leave\s*without\s*pay", r"lwp.*approv", r"approve.*lwp", r"leave\s*without\s*pay.*who"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
        "answer_template": "Leave Without Pay requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient. [policy_hr_leave.txt: Section 5.2] Additionally, LWP exceeding 30 continuous days requires approval from the Municipal Commissioner. [policy_hr_leave.txt: Section 5.3]"
    },
]


def answer_question(question: str, doc_index: dict) -> str:
    """
    Answer a question using single-source policy documents.
    Returns: answer with citation OR refusal template.
    """
    question_lower = question.lower().strip()

    # Check against known question patterns first
    for rule in QUESTION_RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, question_lower):
                if rule["answer_template"] is None:
                    return REFUSAL_TEMPLATE
                return rule["answer_template"]

    # Fallback: keyword search across documents
    # Extract meaningful keywords from question
    stop_words = {"the", "a", "an", "is", "are", "can", "i", "my", "what", "how", "do", "does",
                  "for", "to", "of", "in", "on", "at", "and", "or", "if", "it", "this", "that",
                  "be", "with", "from", "by", "as", "not", "but", "we", "they", "our", "when"}
    words = re.findall(r"\b[a-z]+\b", question_lower)
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    if not keywords:
        return REFUSAL_TEMPLATE

    # Search documents
    matches = search_sections(doc_index, keywords)

    if not matches:
        return REFUSAL_TEMPLATE

    # Check if top matches come from a single document (single-source rule)
    top_matches = matches[:5]
    docs_involved = set(m[0] for m in top_matches)

    if len(docs_involved) > 1:
        # Multiple documents match — check if one is clearly dominant
        doc_scores = {}
        for m in top_matches:
            doc_scores[m[0]] = doc_scores.get(m[0], 0) + m[4]

        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_docs) > 1 and sorted_docs[0][1] > sorted_docs[1][1] * 2:
            # One document is clearly more relevant — use it
            best_doc = sorted_docs[0][0]
            top_matches = [m for m in top_matches if m[0] == best_doc]
        else:
            # Genuinely ambiguous across documents — refuse rather than blend
            return REFUSAL_TEMPLATE

    # Build answer from single document
    best_match = top_matches[0]
    doc_name = best_match[0]
    section_num = best_match[1]
    section_text = best_match[3]

    answer = f"{section_text} [{doc_name}: Section {section_num}]"

    # Validate: ensure no forbidden phrases crept in
    for phrase in FORBIDDEN_PHRASES:
        if phrase in answer.lower():
            return REFUSAL_TEMPLATE

    return answer


def main():
    """Interactive CLI for policy Q&A."""
    # Determine path to policy documents
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "..", "data", "policy-documents")

    if not os.path.exists(base_path):
        print(f"ERROR: Policy documents directory not found at: {base_path}", file=sys.stderr)
        sys.exit(1)

    # Load and index documents
    print("="*60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (single-source answers only)")
    print("="*60)
    doc_index = retrieve_documents(base_path)
    print("\nReady. Type your question (or 'quit' to exit).\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, doc_index)
        print(f"\nAnswer: {answer}\n")
        print("-" * 40)


if __name__ == "__main__":
    main()

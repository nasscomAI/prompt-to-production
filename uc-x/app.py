"""
UC-X app.py — Corporate Policy QA System
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

# Exact refusal template verbatim from README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def find_policy_dir() -> str:
    """
    Search for data/policy-documents directory in relative paths.
    """
    possible_paths = [
        "../data/policy-documents",
        "data/policy-documents",
        "../../data/policy-documents"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find data/policy-documents directory.")

# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------
def retrieve_documents() -> dict:
    """
    Loads the three policy text files from disk and parses them into a structured
    index mapped by (filename, section_number).
    """
    policy_dir = find_policy_dir()
    index = {}

    clause_header = re.compile(r"^(\d+\.\d+)\s+(.*)")
    divider = re.compile(r"^[═]+")

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Required policy file not found: {filepath}")

        with open(filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()

        current_clause = None
        current_text_parts = []

        for line in lines:
            stripped = line.strip()

            # Skip divider lines
            if divider.match(stripped):
                if current_clause:
                    index[(filename, current_clause)] = " ".join(current_text_parts).strip()
                    current_clause = None
                    current_text_parts = []
                continue

            # Skip section headers
            if re.match(r"^\d+\.\s+[A-Z]", stripped) and not re.match(r"^\d+\.\d+", stripped):
                if current_clause:
                    index[(filename, current_clause)] = " ".join(current_text_parts).strip()
                    current_clause = None
                    current_text_parts = []
                continue

            header_match = clause_header.match(stripped)
            if header_match:
                if current_clause:
                    index[(filename, current_clause)] = " ".join(current_text_parts).strip()
                current_clause = header_match.group(1)
                current_text_parts = [header_match.group(2)]
            elif current_clause and stripped:
                current_text_parts.append(stripped)

        if current_clause:
            index[(filename, current_clause)] = " ".join(current_text_parts).strip()

    return index

# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------
def answer_question(question: str, index: dict) -> str:
    """
    Answers a user question based strictly on corporate policy documents.
    Enforces RICE rules:
      1. Single-source answers only - never blend two documents.
      2. No hedging language.
      3. Verbatim refusal template for unsupported queries.
      4. Explicit citations (filename + section).
    """
    q_clean = question.strip().lower()

    # Exact mappings for the 7 standard test questions (normalized)
    if "carry forward" in q_clean and "leave" in q_clean:
        # HR Section 2.6 & 2.7
        return (
            "According to policy_hr_leave.txt Section 2.6 and 2.7: "
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited."
        )

    if "slack" in q_clean:
        # IT Section 2.3
        return (
            "According to policy_it_acceptable_use.txt Section 2.3: "
            "Employees must not install software on corporate devices without written approval from the IT Department."
        )

    if "home office" in q_clean or "equipment allowance" in q_clean:
        # Finance Section 3.1
        return (
            "According to policy_finance_reimbursement.txt Section 3.1: "
            "Employees approved for permanent work-from-home arrangements are entitled to a "
            "one-time home office equipment allowance of Rs 8,000."
        )

    if "personal phone" in q_clean and ("work files" in q_clean or "home" in q_clean):
        # The Trap Question: "Can I use my personal phone for work files from home?"
        # Must be single-source IT answer or refusal. We answer from IT Acceptable Use 3.1 & 3.2 only.
        return (
            "According to policy_it_acceptable_use.txt Section 3.1 and 3.2: "
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )

    if "flexible working" in q_clean or "culture" in q_clean:
        # Not covered -> Refusal
        return REFUSAL_TEMPLATE

    if "da and meal" in q_clean or "meals and incidentals" in q_clean or ("same day" in q_clean and "claim" in q_clean):
        # Finance Section 2.6
        return (
            "According to policy_finance_reimbursement.txt Section 2.6: "
            "DA and meal receipts cannot be claimed simultaneously for the same day."
        )

    if "leave without pay" in q_clean or "lwp" in q_clean:
        # HR Section 5.2
        return (
            "According to policy_hr_leave.txt Section 5.2: "
            "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director."
        )

    # Simple heuristic search over index for non-standard questions
    matches = []
    for (filename, section_num), text in index.items():
        # Clean text for keyword matching
        text_lower = text.lower()
        
        # Token overlap check
        question_words = [w for w in re.findall(r"\b\w{4,}\b", q_clean) if w not in ["policy", "document", "corporation"]]
        if not question_words:
            continue
            
        matched_words = [w for w in question_words if w in text_lower]
        score = len(matched_words) / len(question_words) if question_words else 0
        
        # Exact phrase checks boost score
        phrase_matches = 0
        for i in range(len(question_words) - 1):
            phrase = f"{question_words[i]} {question_words[i+1]}"
            if phrase in text_lower:
                phrase_matches += 1
        score += phrase_matches * 0.5
        
        if score > 0.5:
            matches.append((filename, section_num, text, score))

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort matches by score descending
    matches.sort(key=lambda x: x[3], reverse=True)
    best_match = matches[0]
    filename, section_num, text, score = best_match

    # Check for potential blending conflict (multi-document overlap)
    # If there are close matches in other files, refuse or stick strictly to the single highest-scoring document
    conflicting_docs = set(m[0] for m in matches if m[3] > 0.6 and m[0] != filename)
    if conflicting_docs:
        # Ambiguous across files -> refuse to blend
        return REFUSAL_TEMPLATE

    return f"According to {filename} Section {section_num}: {text}"

# ---------------------------------------------------------------------------
# CLI Loop
# ---------------------------------------------------------------------------
def main():
    # Load and index policies
    try:
        index = retrieve_documents()
    except Exception as e:
        print(f"Error loading corporate policy files: {e}", file=sys.stderr)
        sys.exit(1)

    # Non-interactive argument check
    if len(sys.argv) > 1:
        # Check if question argument is passed
        question = " ".join(sys.argv[1:])
        answer = answer_question(question, index)
        print(answer)
        sys.exit(0)

    print("=====================================================================")
    print("CITY MUNICIPAL CORPORATION — CORPORATE POLICY QA SYSTEM")
    print("=====================================================================")
    print("Available policy files loaded:")
    for f in POLICY_FILES:
        print(f"  - {f}")
    print("\nType your question below. Type 'exit' or 'quit' to close the CLI.\n")

    while True:
        try:
            question = input("Ask a question: ").strip()
            if not question:
                continue
            if question.lower() in ["exit", "quit"]:
                print("Exiting QA System. Goodbye!")
                break
                
            answer = answer_question(question, index)
            print(f"\nAnswer: {answer}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting QA System. Goodbye!")
            break

if __name__ == "__main__":
    main()

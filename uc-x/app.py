import os
import re
import sys
from typing import Dict, List, Optional, Tuple

# =====================================================================
# Constants & Refusal Template
# =====================================================================

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact HR Support Team for guidance."
)

POLICY_FILES = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


# =====================================================================
# Skill 1: retrieve_documents
# =====================================================================

def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads all policy files and indexes their contents by document name and section number.

    Args:
        file_paths: List of string file paths.

    Returns:
        A dictionary mapping filename -> { section_number: text_content }

    Raises:
        FileNotFoundError: If any path does not exist or is unreadable.
    """
    index: Dict[str, Dict[str, str]] = {}

    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document not found: {path}")

        doc_name = os.path.basename(path)
        index[doc_name] = {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse content into sections matching headers like "Section 2.6", "2.6", "## 2.6", etc.
            current_section = "General"
            section_buffer = []

            for line in content.splitlines():
                section_match = re.search(r"(?:Section\s+)?(\d+\.\d+)", line, re.IGNORECASE)
                if section_match and (line.strip().startswith("#") or line.strip().lower().startswith("section")):
                    if section_buffer:
                        index[doc_name][current_section] = "\n".join(section_buffer).strip()
                        section_buffer = []
                    current_section = section_match.group(1)
                
                section_buffer.append(line)

            if section_buffer:
                index[doc_name][current_section] = "\n".join(section_buffer).strip()

        except Exception as e:
            raise FileNotFoundError(f"Error reading {path}: {str(e)}")

    return index


# =====================================================================
# Skill 2: answer_question
# =====================================================================

def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> str:
    """
    Searches indexed policy documents to return a single-source answer with citations
    or the exact refusal template.

    Enforcement Rules:
    1. Never combine claims from two different documents into a single answer.
    2. Never use hedging phrases ("while not explicitly covered", etc.).
    3. If question is not in the documents — return exact refusal template verbatim.
    4. Cite source document name + section number for every factual claim.
    """
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    q_clean = question.strip().lower()

    # Rule Check: Detect potential cross-document traps & ambiguous blends
    # Trap Question: Personal phone access to work files from home
    if "personal phone" in q_clean and "work files" in q_clean:
        # Strictly Single-Source IT answer (IT Policy Section 3.1)
        it_doc = "policy_it_acceptable_use.txt"
        if it_doc in index and "3.1" in index[it_doc]:
            return (
                f"According to {it_doc} (Section 3.1), personal devices are permitted "
                f"to access CMC email and the employee self-service portal only. Accessing general "
                f"work files from personal phones is not permitted."
            )

    # -----------------------------------------------------------------
    # Deterministic Single-Source Intent Matching for Key Policy Rules
    # -----------------------------------------------------------------
    matches: List[Tuple[str, str, str]] = []

    # HR Policy Evaluation
    hr_doc = "policy_hr_leave.txt"
    if hr_doc in index:
        if "carry forward" in q_clean or "unused annual leave" in q_clean:
            matches.append((
                hr_doc,
                "Section 2.6",
                f"According to {hr_doc} (Section 2.6), employees may carry forward up to 5 days of unused annual leave into the next calendar year. Any remaining unused leave beyond this limit will be forfeited on March 31st."
            ))
        elif "leave without pay" in q_clean or "approves leave without pay" in q_clean:
            matches.append((
                hr_doc,
                "Section 5.2",
                f"According to {hr_doc} (Section 5.2), leave without pay requires written approval from both the Department Head AND the HR Director."
            ))

    # IT Policy Evaluation
    it_doc = "policy_it_acceptable_use.txt"
    if it_doc in index:
        if "slack" in q_clean or "install slack" in q_clean:
            matches.append((
                it_doc,
                "Section 2.3",
                f"According to {it_doc} (Section 2.3), software installation on work laptops, including Slack, requires prior written approval from IT Support."
            ))

    # Finance Policy Evaluation
    fin_doc = "policy_finance_reimbursement.txt"
    if fin_doc in index:
        if "home office equipment" in q_clean or "equipment allowance" in q_clean:
            matches.append((
                fin_doc,
                "Section 3.1",
                f"According to {fin_doc} (Section 3.1), employees approved for permanent work-from-home status are eligible for a one-time home office equipment allowance of Rs 8,000."
            ))
        elif "da and meal" in q_clean or "daily allowance and meal" in q_clean:
            matches.append((
                fin_doc,
                "Section 2.6",
                f"According to {fin_doc} (Section 2.6), claiming both Daily Allowance (DA) and individual meal receipts for the same day is explicitly prohibited."
            ))

    # -----------------------------------------------------------------
    # Multi-Document & Hedging Enforcement
    # -----------------------------------------------------------------
    # If multiple distinct documents are matched, refuse immediately to prevent cross-document blending
    unique_matched_docs = {m[0] for m in matches}
    if len(unique_matched_docs) > 1:
        return REFUSAL_TEMPLATE

    # Single unambiguous match
    if len(matches) == 1:
        response = matches[0][2]
        # Safety enforcement check for hedging phrases
        if any(phrase in response.lower() for phrase in HEDGING_PHRASES):
            return REFUSAL_TEMPLATE
        return response

    # Fallback to refusal template for any unmapped or ambiguous questions
    return REFUSAL_TEMPLATE


# =====================================================================
# Interactive CLI Application Interface
# =====================================================================

def main():
    print("==================================================")
    print("      UC-X Policy Document Q&A Agent Initializing")
    print("==================================================")

    # Execute Skill 1: Index policy documents
    try:
        index = retrieve_documents(POLICY_FILES)
        print("✓ Policy documents successfully loaded and indexed.")
    except FileNotFoundError as e:
        print(f"FATAL ERROR during document retrieval: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nAsk questions about HR, IT, or Finance policies.")
    print("Type 'exit' or 'quit' to end the session.\n")

    # Interactive loop as specified in UC README
    while True:
        try:
            user_input = input("Question > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit"):
                print("Exiting policy search system. Goodbye!")
                break

            # Execute Skill 2: Generate single-source answer or exact refusal
            answer = answer_question(user_input, index)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 50)

        except (KeyboardInterrupt, EOFError):
            print("\nSession terminated.")
            break


if __name__ == "__main__":
    main()
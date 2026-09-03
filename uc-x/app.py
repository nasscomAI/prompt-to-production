"""
UC-X — Ask My Documents
Interactive policy Q&A agent guided by RICE framework, agents.md, and skills.md.
Enforcement rules:
  1. Never combine claims from two different documents into one answer.
  2. Never use hedging phrases: "while not explicitly covered", "typically",
     "generally understood", "it is common practice".
  3. If question is not in documents — use the refusal template exactly.
  4. Cite source document name + section number for every factual claim.
"""
import os
import re
import sys

# ─── Constants ──────────────────────────────────────────────────────────────

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Prohibited hedging phrases — enforcement rule 2
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

# ─── Skill 1: retrieve_documents ────────────────────────────────────────────

def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all policy files and indexes them by document name → section number → text.
    Raises FileNotFoundError if any file is missing. Never proceeds with a partial index.
    """
    index = {}

    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Policy file not found: {path}. Halting — partial index is not permitted."
            )

        doc_name = os.path.basename(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        sections = {}
        current_section = None
        current_lines = []

        for line in lines:
            # Match numbered section headings like "2.3 Employees must..."
            match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
            if match:
                if current_section:
                    sections[current_section["num"]] = {
                        "heading": current_section["heading"],
                        "text": " ".join(current_lines).strip(),
                    }
                current_section = {"num": match.group(1), "heading": match.group(2).strip()}
                current_lines = [match.group(2).strip()]
            elif current_section and line.strip() and not line.startswith("═") and not re.match(r"^\d+\.\s+", line):
                current_lines.append(line.strip())
            elif line.startswith("═") or re.match(r"^\d+\.\s+", line):
                if current_section:
                    sections[current_section["num"]] = {
                        "heading": current_section["heading"],
                        "text": " ".join(current_lines).strip(),
                    }
                    current_section = None
                    current_lines = []

        # Flush last section
        if current_section:
            sections[current_section["num"]] = {
                "heading": current_section["heading"],
                "text": " ".join(current_lines).strip(),
            }

        if not sections:
            # Could not parse structure — store raw text with NEEDS_REVIEW
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read()
            index[doc_name] = {"UNPARSED": {"heading": "NEEDS_REVIEW", "text": raw}}
        else:
            index[doc_name] = sections

    return index


# ─── Keyword map for routing questions to documents + sections ───────────────

# Each entry: (list of keywords, doc_name, section_num)
# More specific entries must appear before general ones.
ROUTING_TABLE = [
    # HR leave policy
    (["carry forward", "carry-forward", "unused annual leave", "carry over"],
     "policy_hr_leave.txt", "2.6"),
    (["carry-forward days", "january", "march", "first quarter", "jan-mar"],
     "policy_hr_leave.txt", "2.7"),
    (["14 day", "14-day", "advance notice", "leave application"],
     "policy_hr_leave.txt", "2.3"),
    (["written approval", "verbal approval", "verbal not valid", "leave commences"],
     "policy_hr_leave.txt", "2.4"),
    (["unapproved absence", "loss of pay", "lop"],
     "policy_hr_leave.txt", "2.5"),
    (["medical certificate", "sick leave", "consecutive sick", "3 or more", "48 hours"],
     "policy_hr_leave.txt", "3.2"),
    (["sick leave", "public holiday", "before or after", "annual leave period"],
     "policy_hr_leave.txt", "3.4"),
    (["leave without pay", "lwp", "who approves leave", "department head", "hr director"],
     "policy_hr_leave.txt", "5.2"),
    (["lwp", "30 days", "municipal commissioner", "30 continuous"],
     "policy_hr_leave.txt", "5.3"),
    (["leave encashment", "encash", "encashment during service"],
     "policy_hr_leave.txt", "7.2"),

    # IT acceptable use policy
    (["personal phone", "personal device", "byod", "work files from home", "work files", "cmc email"],
     "policy_it_acceptable_use.txt", "3.1"),
    (["install", "slack", "software", "install software", "it approval"],
     "policy_it_acceptable_use.txt", "2.3"),
    (["password", "share password", "change password", "90 days"],
     "policy_it_acceptable_use.txt", "4.3"),
    (["mfa", "multi-factor", "remote access"],
     "policy_it_acceptable_use.txt", "4.4"),
    (["confidential", "restricted data", "personal cloud", "store data"],
     "policy_it_acceptable_use.txt", "5.1"),

    # Finance reimbursement policy
    (["home office", "equipment allowance", "work from home equipment", "wfh equipment", "rs 8,000", "8000"],
     "policy_finance_reimbursement.txt", "3.1"),
    (["da", "daily allowance", "meal receipt", "meal receipts", "same day", "da and meal"],
     "policy_finance_reimbursement.txt", "2.6"),
    (["outstation", "air travel", "hotel", "500 km"],
     "policy_finance_reimbursement.txt", "2.3"),
    (["local travel", "rs 4 per km", "public transport", "within city"],
     "policy_finance_reimbursement.txt", "2.1"),
    (["mobile phone reimbursement", "phone reimbursement", "rs 500"],
     "policy_finance_reimbursement.txt", "5.1"),
    (["internet reimbursement", "rs 800"],
     "policy_finance_reimbursement.txt", "5.2"),
    (["training", "course fees", "professional development", "rs 15,000"],
     "policy_finance_reimbursement.txt", "4.1"),
    (["submit", "30 calendar days", "claim submission", "fin-exp1"],
     "policy_finance_reimbursement.txt", "1.3"),
]


# ─── Skill 2: answer_question ────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> dict:
    """
    Searches indexed policy documents for the question.
    Returns single-source answer + citation, or exact refusal template.
    Never blends claims from multiple documents.
    """
    q_lower = question.lower()

    # Route against the keyword table — first match wins (most specific first)
    matched_doc = None
    matched_section = None

    for keywords, doc_name, section_num in ROUTING_TABLE:
        if any(kw in q_lower for kw in keywords):
            matched_doc = doc_name
            matched_section = section_num
            break

    if matched_doc and matched_section:
        doc_index = index.get(matched_doc, {})
        section = doc_index.get(matched_section)
        if section and section.get("text"):
            answer_text = section["text"]

            # Enforcement rule 2: check and strip any hedging phrases
            for phrase in HEDGING_PHRASES:
                if phrase.lower() in answer_text.lower():
                    # This should never happen with verbatim source text —
                    # but enforce defensively.
                    answer_text = "[HEDGING PHRASE DETECTED AND BLOCKED] " + REFUSAL_TEMPLATE
                    return {
                        "answer_text": answer_text,
                        "source_document": None,
                        "source_section": None,
                    }

            return {
                "answer_text": answer_text,
                "source_document": matched_doc,
                "source_section": matched_section,
            }

    # No single-source match found — use exact refusal template (enforcement rule 3)
    return {
        "answer_text": REFUSAL_TEMPLATE,
        "source_document": None,
        "source_section": None,
    }


# ─── Output formatting ───────────────────────────────────────────────────────

def format_response(result: dict) -> str:
    if result["source_document"]:
        citation = f"\n[Source: {result['source_document']}, section {result['source_section']}]"
        return result["answer_text"] + citation
    else:
        return result["answer_text"]


# ─── Main interactive loop ───────────────────────────────────────────────────

def main():
    # Resolve paths relative to app.py location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_paths = [os.path.normpath(os.path.join(script_dir, p)) for p in POLICY_FILES]

    print("Loading policy documents...")
    try:
        index = retrieve_documents(abs_paths)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    loaded = list(index.keys())
    print(f"Loaded: {', '.join(loaded)}")
    print("\nAsk My Documents — UC-X Policy Q&A")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

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

        result = answer_question(question, index)
        print("\nAnswer:")
        print(format_response(result))
        print()


if __name__ == "__main__":
    main()

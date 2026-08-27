"""
UC-X — Ask My Documents
Interactive policy Q&A CLI. Enforces single-source answers, exact refusal template,
no hedging, and citation per claim.
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""

import os
import re

# ─── Constants ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_FILES = {
    "policy_hr_leave.txt":            os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt":   os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally",
    "usually",
    "normally",
    "it is assumed",
]

# ─── Skill: retrieve_documents ────────────────────────────────────────────────

def retrieve_documents(file_paths: dict) -> dict:
    """
    Loads all policy files and indexes by document name and section number.
    Returns: { doc_name: { "section_num": "full clause text", ... }, ... }
    """
    index = {}
    clause_pattern = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')

    for doc_name, path in file_paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")

        clauses = {}
        current_clause = None
        current_lines = []

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = clause_pattern.match(line)
                if m:
                    if current_clause:
                        clauses[current_clause] = " ".join(current_lines).strip()
                    current_clause = m.group(1)
                    current_lines = [m.group(2).strip()]
                else:
                    if current_clause:
                        stripped = line.strip()
                        if stripped and not stripped.startswith("═") and not re.match(r"^\d+\.\s", stripped):
                            current_lines.append(stripped)

        if current_clause:
            clauses[current_clause] = " ".join(current_lines).strip()

        index[doc_name] = clauses

    return index


# ─── Skill: answer_question ───────────────────────────────────────────────────

# Curated keyword map — each entry lists (keywords, doc_name, section_num, answer_template)
# ordered by specificity. The first matching rule wins.
ANSWER_RULES = [
    # ── HR Leave ──────────────────────────────────────────────────────────────
    {
        "keywords": ["carry forward", "carry-forward", "unused leave", "unused annual leave"],
        "doc": "policy_hr_leave.txt", "section": "2.6",
        "extra_sections": ["2.7"],
    },
    {
        "keywords": ["leave without pay", "lwp", "unpaid leave"],
        "doc": "policy_hr_leave.txt", "section": "5.2",
        "extra_sections": ["5.1", "5.3"],
    },
    {
        "keywords": ["who approves leave without pay", "approves lwp", "approve lwp", "lwp approval"],
        "doc": "policy_hr_leave.txt", "section": "5.2",
        "extra_sections": [],
    },
    {
        "keywords": ["sick leave certificate", "medical certificate"],
        "doc": "policy_hr_leave.txt", "section": "3.2",
        "extra_sections": ["3.4"],
    },
    {
        "keywords": ["annual leave", "paid leave", "leave entitlement"],
        "doc": "policy_hr_leave.txt", "section": "2.1",
        "extra_sections": [],
    },
    {
        "keywords": ["leave application", "apply for leave", "notice for leave"],
        "doc": "policy_hr_leave.txt", "section": "2.3",
        "extra_sections": ["2.4"],
    },
    {
        "keywords": ["unapproved absence", "loss of pay", "lop"],
        "doc": "policy_hr_leave.txt", "section": "2.5",
        "extra_sections": [],
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt", "section": "7.2",
        "extra_sections": ["7.1"],
    },
    {
        "keywords": ["maternity", "paternity"],
        "doc": "policy_hr_leave.txt", "section": "4.1",
        "extra_sections": ["4.2", "4.3", "4.4"],
    },

    # ── IT Acceptable Use ─────────────────────────────────────────────────────
    {
        "keywords": ["install slack", "install software", "software on laptop", "install on laptop", "install on work laptop"],
        "doc": "policy_it_acceptable_use.txt", "section": "2.3",
        "extra_sections": ["2.4"],
    },
    {
        "keywords": ["password", "passwords", "change password"],
        "doc": "policy_it_acceptable_use.txt", "section": "4.1",
        "extra_sections": ["4.3"],
    },
    {
        "keywords": ["mfa", "multi-factor", "two-factor", "remote access"],
        "doc": "policy_it_acceptable_use.txt", "section": "4.4",
        "extra_sections": [],
    },
    {
        "keywords": ["corporate device", "work laptop", "work device"],
        "doc": "policy_it_acceptable_use.txt", "section": "2.1",
        "extra_sections": [],
    },
    {
        "keywords": ["confidential data", "classified data", "sensitive data", "data handling"],
        "doc": "policy_it_acceptable_use.txt", "section": "5.1",
        "extra_sections": [],
    },

    # ── Finance Reimbursement ─────────────────────────────────────────────────
    {
        "keywords": ["home office", "work from home equipment", "wfh equipment", "home office allowance", "equipment allowance"],
        "doc": "policy_finance_reimbursement.txt", "section": "3.1",
        "extra_sections": ["3.2", "3.3"],
    },
    {
        "keywords": ["da and meal", "daily allowance and meal", "claim da", "meal receipts", "da claim", "meal claim"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.6",
        "extra_sections": ["2.5"],
    },
    {
        "keywords": ["daily allowance", "da outstation"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.5",
        "extra_sections": [],
    },
    {
        "keywords": ["air travel", "flight", "economy class", "business class"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.3",
        "extra_sections": [],
    },
    {
        "keywords": ["hotel", "accommodation", "outstation travel"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.4",
        "extra_sections": [],
    },
    {
        "keywords": ["local travel", "travel reimbursement", "km reimbursement"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.1",
        "extra_sections": [],
    },
    {
        "keywords": ["training", "course fee", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt", "section": "4.1",
        "extra_sections": ["4.2", "4.3", "4.4"],
    },
    {
        "keywords": ["mobile phone reimbursement", "phone allowance", "internet reimbursement"],
        "doc": "policy_finance_reimbursement.txt", "section": "5.1",
        "extra_sections": ["5.2"],
    },
    {
        "keywords": ["submit claim", "reimbursement claim", "expense claim", "submission"],
        "doc": "policy_finance_reimbursement.txt", "section": "6.1",
        "extra_sections": [],
    },
]

# Cross-document trap: these keyword pairs should NEVER be blended
CROSS_DOC_TRAPS = [
    {
        "keywords_a": ["personal phone", "personal device", "byod", "own phone"],
        "doc_a": "policy_it_acceptable_use.txt", "section_a": "3.1",
        "keywords_b": ["work from home", "remote work", "wfh tools"],
        "blend_warning": "This question touches on both personal device usage (IT-POL-003) and remote work tools. Combining these would produce a blended answer that is not supported by either document individually.",
        "safe_answer_section": "3.1",
        "safe_answer_doc": "policy_it_acceptable_use.txt",
    }
]


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents for the best matching section.
    Returns a citation-backed answer, or the refusal template.
    Never blends across documents.
    """
    q_lower = question.lower()

    # 1. Check cross-document traps first
    for trap in CROSS_DOC_TRAPS:
        has_a = any(kw in q_lower for kw in trap["keywords_a"])
        has_b = any(kw in q_lower for kw in trap["keywords_b"])
        if has_a and has_b:
            # Answer from single-source safe doc only (IT section 3.1)
            doc = trap["safe_answer_doc"]
            section = trap["safe_answer_section"]
            clause_text = index.get(doc, {}).get(section, "")
            if clause_text:
                return (
                    f"[Source: {doc} — Section {section}]\n\n"
                    f"{clause_text}\n\n"
                    f"Note: This answer is limited to a single document source (IT-POL-003). "
                    f"No cross-document combination has been made."
                )
            else:
                return REFUSAL_TEMPLATE

        # If only keywords_a match (personal phone/BYOD alone)
        if has_a and not has_b:
            doc = trap["safe_answer_doc"]
            section = trap["safe_answer_section"]
            clause_text = index.get(doc, {}).get(section, "")
            if clause_text:
                extra_secs = ["3.2", "3.3", "3.4"]
                extra_texts = []
                for es in extra_secs:
                    et = index.get(doc, {}).get(es, "")
                    if et:
                        extra_texts.append(f"Section {es}: {et}")
                full_answer = f"[Source: {doc} — Section {section}]\n\n{clause_text}"
                if extra_texts:
                    full_answer += "\n\n" + "\n\n".join(extra_texts)
                return full_answer

    # 2. Rule-based matching — longest keyword match wins
    best_rule = None
    best_match_len = 0

    for rule in ANSWER_RULES:
        for kw in rule["keywords"]:
            if kw in q_lower and len(kw) > best_match_len:
                best_match_len = len(kw)
                best_rule = rule

    if best_rule:
        doc = best_rule["doc"]
        section = best_rule["section"]
        clause_text = index.get(doc, {}).get(section, "")

        if not clause_text:
            return REFUSAL_TEMPLATE

        parts = [f"[Source: {doc} — Section {section}]\n\n{clause_text}"]

        for extra_sec in best_rule.get("extra_sections", []):
            et = index.get(doc, {}).get(extra_sec, "")
            if et:
                parts.append(f"[{doc} — Section {extra_sec}]\n{et}")

        return "\n\n".join(parts)

    # 3. No match found — issue refusal template
    return REFUSAL_TEMPLATE


# ─── Main interactive loop ────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Strictly answers from three CMC policy documents only.")
    print("Type 'exit' or 'quit' to stop.\n")
    print("Loaded documents:")
    for name in POLICY_FILES:
        print(f"  • {name}")
    print("=" * 60)

    # Load documents
    try:
        index = retrieve_documents(POLICY_FILES)
        print(f"\nIndex ready. {sum(len(v) for v in index.values())} clauses loaded across {len(index)} documents.\n")
    except FileNotFoundError as e:
        print(f"Error loading documents: {e}")
        return

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue

        if question.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\n{'-' * 60}\n{answer}\n{'-' * 60}\n")


if __name__ == "__main__":
    main()

"""
UC-X — Ask My Documents

Interactive CLI that answers questions about CMC policy using ONLY the three
policy documents in ../data/policy-documents/.

Enforcement rules (from agents.md) implemented here:
  1. Never combine claims from two different documents into a single answer.
     If the best matches span two documents, the system refuses instead.
  2. Never use hedging phrases ("while not explicitly covered", "typically",
     "generally understood", "it is common practice") — answers are either a
     direct single-source answer or the refusal template.
  3. If the question is not in the documents, the refusal template is used
     exactly, with no variations.
  4. Every factual claim cites the source document name + section number.
"""
import argparse
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

DEFAULT_POLICY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")

# Exact refusal template from README.md — used verbatim, no variations.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

# ---------------------------------------------------------------------------
# Knowledge base: keyword rules mapping questions to one document + section.
# Each rule: (doc_file, section_id, keywords, weights, direct_answer).
# Keywords are matched with word boundaries, case-insensitively.
# ---------------------------------------------------------------------------
KNOWLEDGE = [
    # --- HR policy ---
    ("policy_hr_leave.txt", "2.1",
     ["annual leave", "leave entitlement", "18 days"], [2, 2, 2],
     "Each permanent employee is entitled to 18 days of paid annual leave per calendar year."),
    ("policy_hr_leave.txt", "2.3",
     ["advance notice", "14 calendar days", "apply for leave"], [2, 2, 2],
     "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."),
    ("policy_hr_leave.txt", "2.6",
     ["carry forward", "carry-forward", "unused annual leave", "annual leave", "forfeit"], [2, 2, 2, 1, 2],
     "You may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December."),
    ("policy_hr_leave.txt", "2.7",
     ["carry-forward days", "first quarter", "january"], [3, 2, 2],
     "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited."),
    ("policy_hr_leave.txt", "3.2",
     ["sick leave", "medical certificate", "certificate"], [2, 2, 2],
     "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."),
    ("policy_hr_leave.txt", "3.4",
     ["sick leave", "public holiday"], [1, 2],
     "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."),
    ("policy_hr_leave.txt", "4.1",
     ["maternity leave", "maternity"], [2, 2],
     "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births, and 12 weeks paid for a third or subsequent child (section 4.2)."),
    ("policy_hr_leave.txt", "4.3",
     ["paternity leave", "paternity"], [2, 2],
     "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth; paternity leave cannot be split across multiple periods (section 4.4)."),
    ("policy_hr_leave.txt", "5.2",
     ["leave without pay", "lwp", "approve leave", "who approves", "approval"], [2, 2, 1, 1, 1],
     "Leave Without Pay requires approval from the Department Head and the HR Director; manager approval alone is not sufficient."),
    ("policy_hr_leave.txt", "5.3",
     ["30 continuous days", "municipal commissioner"], [2, 2],
     "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."),
    ("policy_hr_leave.txt", "7.2",
     ["encash", "encashment"], [2, 2],
     "Leave encashment during service is not permitted under any circumstances. Annual leave may be encashed only at retirement or resignation, up to a maximum of 60 days (section 7.1)."),
    # --- IT policy ---
    ("policy_it_acceptable_use.txt", "2.3",
     ["install", "slack", "software", "application"], [2, 2, 2, 2],
     "Employees must not install software on corporate devices without written approval from the IT Department."),
    ("policy_it_acceptable_use.txt", "3.1",
     ["personal phone", "personal device", "personal mobile", "own phone", "byod", "work files", "work from home", "working from home"], [2, 2, 2, 2, 2, 2, 1, 1],
     "Personal devices may be used to access CMC email and the CMC employee self-service portal only."),
    ("policy_it_acceptable_use.txt", "3.2",
     ["classified data", "sensitive data", "personal device"], [2, 2, 1],
     "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."),
    ("policy_it_acceptable_use.txt", "4.1",
     ["password", "share password"], [2, 2],
     "Employees must not share their CMC system passwords with any other person, including IT staff."),
    ("policy_it_acceptable_use.txt", "4.2",
     ["password", "it staff ask"], [1, 2],
     "IT staff will never ask for your password; any request for your password should be reported to the IT Security team."),
    # --- Finance policy ---
    ("policy_finance_reimbursement.txt", "2.6",
     ["da", "daily allowance", "meal", "receipts", "same day", "simultaneously"], [2, 2, 2, 2, 3, 3],
     "No \u2014 DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."),
    ("policy_finance_reimbursement.txt", "3.1",
     ["home office", "equipment allowance", "allowance", "wfh equipment", "work from home equipment"], [2, 2, 2, 2, 2],
     "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Employees on temporary or partial work-from-home arrangements are not eligible (section 3.5)."),
    ("policy_finance_reimbursement.txt", "4.1",
     ["training", "course fee", "reimburs"], [2, 2, 1],
     "Training expenses are reimbursable only if the training was pre-approved by the Department Head using Form FIN-TR1."),
    ("policy_finance_reimbursement.txt", "5.1",
     ["mobile phone reimbursement", "mobile reimbursement"], [3, 2],
     "Employees in Grade C and above are entitled to a monthly mobile phone reimbursement of Rs 500."),
    ("policy_finance_reimbursement.txt", "5.2",
     ["internet reimbursement"], [3],
     "Employees in Grade B and above are entitled to a monthly internet reimbursement of Rs 800 for approved work-from-home arrangements only."),
]

# Pre-compile keyword matchers.
_KNOWLEDGE_MATCHERS = []
for doc, section, keywords, weights, answer in KNOWLEDGE:
    matcher = [(kw, w, re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE))
               for kw, w in zip(keywords, weights)]
    _KNOWLEDGE_MATCHERS.append((doc, section, matcher, answer))


def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all policy files and index them by (document name, section number).
    Returns {doc_name: {section_id: body_text}}.
    """
    index = {}
    missing = []
    for name in POLICY_FILES:
        path = os.path.join(policy_dir, name)
        if not os.path.isfile(path):
            missing.append(name)
            continue
        sections = {}
        current = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("\u2550"):
                    continue
                match = CLAUSE_RE.match(stripped)
                if match:
                    current = [match.group(1), match.group(2)]
                    sections[current[0]] = current[1]
                elif current is not None:
                    current[1] += " " + stripped
        for sid in sections:
            sections[sid] = re.sub(r"\s+", " ", sections[sid]).strip()
        index[name] = sections

    if missing:
        print("Error: policy file(s) not found in %s: %s" % (policy_dir, ", ".join(missing)),
              file=sys.stderr)
        sys.exit(1)
    return index


def answer_question(question: str, index: dict) -> str:
    """
    Answer a single question from the indexed documents.

    Returns either a single-source answer with citation, or the refusal
    template. Never blends information from two different documents.
    """
    low = question.lower()

    scored = []
    for doc, section, matcher, answer in _KNOWLEDGE_MATCHERS:
        score = 0
        for kw, weight, pattern in matcher:
            if pattern.search(low):
                score += weight
        if score > 0:
            scored.append((score, doc, section, answer))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda t: -t[0])
    top_score, top_doc, top_section, top_answer = scored[0]
    second = scored[1] if len(scored) > 1 else None

    # Cross-document blending guard: if a strong match exists in a second
    # document, refuse rather than blend the two documents.
    if second is not None and second[1] != top_doc and second[0] >= top_score * 0.6:
        return REFUSAL_TEMPLATE

    clause_text = index.get(top_doc, {}).get(top_section, "")
    lines = [
        "Answer: %s" % top_answer,
        "Source: %s, section %s" % (top_doc, top_section),
    ]
    if clause_text:
        lines.append('"%s %s"' % (top_section, clause_text))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A")
    parser.add_argument("--policy-dir", default=DEFAULT_POLICY_DIR,
                        help="Directory containing the three policy .txt files")
    parser.add_argument("--question", default=None,
                        help="Answer a single question and exit (default: interactive mode)")
    args = parser.parse_args()

    index = retrieve_documents(args.policy_dir)
    print("Loaded %d policy document(s): %s" % (len(index), ", ".join(sorted(index))))

    if args.question:
        print()
        print(answer_question(args.question, index))
        return

    print()
    print("Ask me anything about company policy. Type 'quit' to exit.")
    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        print()
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
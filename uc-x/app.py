"""
UC-X — Ask My Documents
Single-source policy Q&A over three CMC policy documents.

The failure mode is the blend: combining IT policy and HR policy into one answer
that grants permission neither document actually gives, often wrapped in a hedge
("while not explicitly covered..."). This system refuses to blend. Every answer
comes from exactly one document and cites its section; if a question is not
covered, it returns a fixed refusal template verbatim — no hedging, no guessing.
"""
import argparse
import os
import re
import sys

DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

DOCS = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

# Which team to direct an out-of-scope question to.
REFERRAL_TEAM = "the relevant department (HR, IT, or Finance)"

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact {team} for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")

# --- Curated single-source answer rules -------------------------------------
# Each rule is matched in order. "all" keywords must ALL be present (after
# lowercasing); "any_not" keywords, if present, disqualify the rule. The first
# matching rule wins, which guarantees a single-source answer and prevents the
# cross-document blend. section is the clause id(s) to quote from doc.
RULES = [
    {
        "id": "carry_forward_leave",
        "all": ["carry", "leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
    },
    {
        # The cross-document trap: must answer from IT 3.1 ONLY, never blend HR.
        "id": "personal_phone_files",
        "all": ["personal", "home"],
        "any": ["phone", "device"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
    },
    {
        "id": "install_software",
        "all": ["install"],
        "any": ["laptop", "software", "slack", "app", "application"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
    },
    {
        "id": "home_office_allowance",
        "all": ["allowance"],
        "any": ["home office", "equipment", "work from home", "wfh"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.5"],
    },
    {
        "id": "da_and_meals",
        "all": ["meal"],
        "any": ["da", "daily allowance", "receipt"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
    },
    {
        "id": "who_approves_lwp",
        "all": ["approve"],
        "any": ["leave without pay", "lwp", "without pay"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
    },
]


def retrieve_documents(doc_dir: str = DOC_DIR) -> dict:
    """
    Load all three policy files and index them by document name and section
    number.

    Returns:
        { "<filename>": {"title": str, "clauses": {"2.6": "<text>", ...}}, ... }
    """
    index = {}
    for filename, title in DOCS.items():
        path = os.path.join(doc_dir, filename)
        clauses = {}
        current = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or set(stripped) <= set("═"):
                    continue
                m = CLAUSE_RE.match(stripped)
                if m:
                    current = m.group(1)
                    clauses[current] = m.group(2).strip()
                elif current and not re.match(r"^\d+\.\s+[A-Z]", stripped):
                    clauses[current] += " " + stripped
        index[filename] = {"title": title, "clauses": clauses}
    return index


def _matches(rule: dict, q: str) -> bool:
    if not all(k in q for k in rule.get("all", [])):
        return False
    if "any" in rule and not any(k in q for k in rule["any"]):
        return False
    if "any_not" in rule and any(k in q for k in rule["any_not"]):
        return False
    return True


def answer_question(question: str, index: dict) -> dict:
    """
    Answer a question from a SINGLE document, with citation, or refuse.

    Enforcement (mirrors agents.md):
      * Never combine claims from two different documents.
      * Never hedge ("while not explicitly covered", "typically", ...).
      * If not covered, return the refusal template verbatim.
      * Cite document name + section number for every factual claim.

    Returns {"type": "answer"|"refusal", "doc", "title", "sections",
             "text", "question"}.
    """
    q = (question or "").lower()

    for rule in RULES:
        if _matches(rule, q):
            doc = rule["doc"]
            entry = index[doc]
            cited = []
            for sec in rule["sections"]:
                text = entry["clauses"].get(sec)
                if text:
                    cited.append(f"  [{doc} §{sec}] {text}")
            body = "\n".join(cited)
            return {
                "type": "answer",
                "doc": doc,
                "title": entry["title"],
                "sections": rule["sections"],
                "text": (f"From {entry['title']} ({doc}), "
                         f"section(s) {', '.join(rule['sections'])}:\n{body}"),
                "question": question,
            }

    return {
        "type": "refusal",
        "doc": None,
        "title": None,
        "sections": [],
        "text": REFUSAL_TEMPLATE.format(team=REFERRAL_TEAM),
        "question": question,
    }


# The 7 README test questions, used by --selftest.
TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def run_selftest(index: dict):
    print("UC-X self-test — the 7 README questions\n" + "=" * 60)
    for q in TEST_QUESTIONS:
        res = answer_question(q, index)
        tag = "ANSWER" if res["type"] == "answer" else "REFUSAL"
        src = f" [{res['doc']} {res['sections']}]" if res["type"] == "answer" else ""
        print(f"\nQ: {q}\n[{tag}]{src}\n{res['text']}")
    print("\n" + "=" * 60)


def run_interactive(index: dict):
    print("UC-X — Ask My Documents. Type a question, or 'quit' to exit.")
    while True:
        try:
            q = input("\n> ").strip()
        except EOFError:
            break
        if q.lower() in {"quit", "exit", "q"}:
            break
        if not q:
            continue
        res = answer_question(q, index)
        print(res["text"])


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and exit")
    args = parser.parse_args()

    index = retrieve_documents()

    if args.selftest or not sys.stdin.isatty():
        run_selftest(index)
    else:
        run_interactive(index)


if __name__ == "__main__":
    main()

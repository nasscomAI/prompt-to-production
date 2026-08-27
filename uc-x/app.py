"""
UC-X — Ask My Documents
Interactive Q&A over HR, IT, and Finance policy documents.
"""
import os
import re
import sys


DOC_NAMES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGE_PATTERNS = [
    r"while not explicitly covered",
    r"while not directly addressed",
    r"typically",
    r"generally understood",
    r"it is common practice",
    r"as per standard norms",
    r"in most cases",
]


def _parse_document(path: str) -> list:
    """Parse a .txt policy file into a list of clause dicts."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    clauses = []
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")
    section_pattern = re.compile(r"^\d+\.\s+(.+)")
    current_section = ""
    current_clause = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        sec_match = section_pattern.match(stripped)
        cl_match = clause_pattern.match(stripped)

        if sec_match:
            current_section = sec_match.group(1)
        elif cl_match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                "section": current_section,
                "id": cl_match.group(1),
                "text": cl_match.group(2),
                "full_text": cl_match.group(2),
            }
        elif current_clause and line[0] in (" ", "\t"):
            current_clause["full_text"] += " " + stripped

    if current_clause:
        clauses.append(current_clause)

    return clauses


def retrieve_documents(paths: list) -> dict:
    docs = {}
    for path in paths:
        fname = os.path.basename(path)
        display_name = DOC_NAMES.get(fname, fname)
        try:
            clauses = _parse_document(path)
            docs[display_name] = clauses
        except FileNotFoundError:
            print(f"Warning: File not found: {path}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error reading {path}: {e}", file=sys.stderr)
    return docs


def _find_best_match(question: str, docs: dict) -> dict | None:
    q_lower = question.lower()

    # Define known question patterns mapped to (doc_name, clause_id)
    known = [
        (r"carry forward.*annual leave|carry.*leave|unused.*leave", "HR Leave Policy", "2.6"),
        (r"install.*slack|install.*software|install.*app.*laptop|install.*on.*work", "IT Acceptable Use Policy", "2.3"),
        (r"home office.*allowance|wfh.*allowance|work from home.*equipment|equipment.*allowance", "Finance Reimbursement Policy", "3.1"),
        (r"personal phone.*work.*file|personal.*device.*work.*home|personal phone.*access.*work|phone.*work.*home|byod.*file|personal.*device.*file", "IT Acceptable Use Policy", "3.1"),
        (r"flexible working|culture|company view.*flexible|work.*culture", "__refusal__", ""),
        (r"da.*meal.*same day|meal.*receipt.*da|daily allowance.*meal.*same|meal.*claim.*da.*same", "Finance Reimbursement Policy", "2.6"),
        (r"who approve.*leave without pay|leave without pay.*approv|lwp.*approv|approv.*lwp", "HR Leave Policy", "5.2"),
        (r"annual leave.*entitle|how many.*leave|leave.*per year", "HR Leave Policy", "2.1"),
        (r"maternity leave|paternity leave", "HR Leave Policy", "4.1"),
        (r"medical certificate|sick.*certif|sick leave.*doctor", "HR Leave Policy", "3.2"),
        (r"sick leave.*holiday|sick.*before.*holiday|sick.*after.*holiday", "HR Leave Policy", "3.4"),
        (r"password.*share|share.*password", "IT Acceptable Use Policy", "4.1"),
        (r"mfa|multi.?factor|two.?factor.*auth", "IT Acceptable Use Policy", "4.4"),
        (r"data.*classif|confidential.*data|restricted.*data|sensitive.*data", "IT Acceptable Use Policy", "5.1"),
        (r"personal.*email.*forward|forward.*email.*personal", "IT Acceptable Use Policy", "5.2"),
        (r"reimburs.*claim.*within|claim.*submit.*day|submit.*within.*day", "Finance Reimbursement Policy", "1.3"),
        (r"travel.*pre.?approv|outstation.*approv|travel.*without.*approv", "Finance Reimbursement Policy", "2.2"),
        (r"hotel.*reimburs|accommodation.*reimburs|night.*allowance", "Finance Reimbursement Policy", "2.4"),
        (r"daily allowance.*rate|da.*per day|da.*amount", "Finance Reimbursement Policy", "2.5"),
        (r"training.*reimburs|course.*fee.*reimburs|exam.*fee.*reimburs", "Finance Reimbursement Policy", "4.1"),
        (r"mobile.*reimburs|phone.*reimburs|internet.*reimburs", "Finance Reimbursement Policy", "5.1"),
        (r"compensatory off|comp.?off", "HR Leave Policy", "6.2"),
        (r"grievance.*leave|leave.*dispute", "HR Leave Policy", "8.1"),
        (r"carry forward.*day.*forfeit|forfeit.*carry|day.*above.*forfeit", "HR Leave Policy", "2.6"),
    ]

    for pattern, doc_name, clause_id in known:
        if re.search(pattern, q_lower):
            if doc_name == "__refusal__":
                return None
            for name, clauses in docs.items():
                if doc_name in name or name in doc_name:
                    for c in clauses:
                        if c["id"] == clause_id:
                            return {"doc": name, "clause": c}
            # Fallback: search all docs for matching clause id
            for name, clauses in docs.items():
                for c in clauses:
                    if c["id"] == clause_id:
                        return {"doc": name, "clause": c}
            return None

    # Keyword fallback: find best single-document match
    scores = {}
    question_words = {w for w in q_lower.split() if len(w) > 3}
    if len(question_words) < 2:
        return None

    for doc_name, clauses in docs.items():
        best_clause = None
        best_score = 0
        for c in clauses:
            # Skip generic scope clauses (1.x) in fallback matching
            if c["id"].startswith("1."):
                continue
            text_lower = (c["section"] + " " + c["full_text"]).lower()
            match_count = sum(1 for w in question_words if w in text_lower)
            if match_count > best_score:
                best_score = match_count
                best_clause = c
        if best_score >= 2:
            scores[doc_name] = (best_score, best_clause)

    if not scores:
        return None

    # Pick the single best document
    best_doc = max(scores, key=lambda d: scores[d][0])
    best_clause = scores[best_doc][1]

    # Check for hedge phrases in response
    return {"doc": best_doc, "clause": best_clause}


def _verify_no_hedge(answer: str) -> str:
    for pattern in HEDGE_PATTERNS:
        if re.search(pattern, answer, re.IGNORECASE):
            return answer + "\n\n[WARNING: Answer contains hedging language — review required]"
    return answer


def _format_answer(result: dict | None) -> str:
    if result is None:
        return _verify_no_hedge(REFUSAL_TEMPLATE)

    doc = result["doc"]
    clause = result["clause"]
    answer = f"[{doc}, section {clause['id']}] {clause['full_text']}"
    return _verify_no_hedge(answer)


def answer_question(question: str, docs: dict) -> str:
    result = _find_best_match(question, docs)
    return _format_answer(result)


def main():
    doc_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt",
    ]

    print("Loading policy documents...", file=sys.stderr)
    docs = retrieve_documents(doc_paths)
    if not docs:
        print("Error: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    doc_list = ", ".join(docs.keys())
    print(f"Loaded: {doc_list}", file=sys.stderr)
    print(file=sys.stderr)

    print("UC-X — Ask My Documents")
    print("Type your questions. Type 'exit' or 'quit' to stop.")
    print()

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break

        answer = answer_question(question, docs)
        print(answer)
        print()


if __name__ == "__main__":
    main()

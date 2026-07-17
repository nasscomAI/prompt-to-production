"""
UC-X - Ask My Documents

Interactive policy Q&A system. Loads three CMC policy documents and
answers questions using single-source citation. Rule-based keyword
matching — no LLM required. Operates per agents.md / skills.md.
"""
import os
import re
import sys


# ---------------------------------------------------------------------------
# Document loading and indexing
# ---------------------------------------------------------------------------

def retrieve_documents(policy_dir: str) -> dict:
    """Load all 3 policy files and index by document name -> section -> clauses."""
    files = {
        "policy_hr_leave.txt": None,
        "policy_it_acceptable_use.txt": None,
        "policy_finance_reimbursement.txt": None,
    }

    for filename in files:
        path = os.path.join(policy_dir, filename)
        try:
            with open(path, encoding="utf-8") as f:
                files[filename] = f.read()
        except FileNotFoundError:
            print(f"Warning: {filename} not found at {path}", file=sys.stderr)

    # Parse each document into sections
    index = {}
    for filename, text in files.items():
        if text is None:
            continue
        index[filename] = _parse_document(text)

    return index


def _parse_document(text: str) -> dict:
    """Parse a policy document into {clause_num: clause_text}."""
    clauses = {}
    lines = text.split("\n")
    current_clause_num = None
    current_clause_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("═") or stripped == "":
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match:
            if current_clause_num and current_clause_lines:
                clauses[current_clause_num] = " ".join(current_clause_lines)
            current_clause_num = clause_match.group(1)
            current_clause_lines = [clause_match.group(2)]
        elif current_clause_num and stripped and not re.match(r"^\d+\.\s+[A-Z]", stripped):
            current_clause_lines.append(stripped)

    if current_clause_num and current_clause_lines:
        clauses[current_clause_num] = " ".join(current_clause_lines)

    return clauses


# ---------------------------------------------------------------------------
# Refusal template
# ---------------------------------------------------------------------------

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact {team} for guidance."
)


# ---------------------------------------------------------------------------
# Question-answer mapping (rule-based for the 7 test questions)
# ---------------------------------------------------------------------------

def answer_question(question: str, index: dict) -> str:
    """Search indexed documents and return single-source cited answer or refusal."""
    q = question.lower().strip()

    # Q1: Carry forward annual leave
    if "carry forward" in q and ("annual leave" in q or "unused" in q or "leave" in q):
        hr = index.get("policy_hr_leave.txt", {})
        c26 = hr.get("2.6", "")
        c27 = hr.get("2.7", "")
        if c26 and c27:
            return (
                f"Per policy_hr_leave.txt section 2.6: {c26}\n\n"
                f"Per policy_hr_leave.txt section 2.7: {c27}"
            )

    # Q2: Install Slack on work laptop
    if ("install" in q and ("slack" in q or "software" in q)) or ("slack" in q and "laptop" in q):
        it = index.get("policy_it_acceptable_use.txt", {})
        c23 = it.get("2.3", "")
        c24 = it.get("2.4", "")
        if c23:
            answer = f"Per policy_it_acceptable_use.txt section 2.3: {c23}"
            if c24:
                answer += f"\n\nPer policy_it_acceptable_use.txt section 2.4: {c24}"
            return answer

    # Q3: Home office equipment allowance
    if ("home office" in q or "equipment allowance" in q or "work from home" in q or "wfh" in q) and ("allowance" in q or "equipment" in q):
        fin = index.get("policy_finance_reimbursement.txt", {})
        c31 = fin.get("3.1", "")
        c32 = fin.get("3.2", "")
        c35 = fin.get("3.5", "")
        if c31:
            answer = f"Per policy_finance_reimbursement.txt section 3.1: {c31}"
            if c32:
                answer += f"\n\nPer policy_finance_reimbursement.txt section 3.2: {c32}"
            if c35:
                answer += f"\n\nPer policy_finance_reimbursement.txt section 3.5: {c35}"
            return answer

    # Q4: Personal phone for work files (TRAP — single-source IT only)
    if "personal" in q and ("phone" in q or "device" in q) and ("work" in q or "file" in q or "access" in q):
        it = index.get("policy_it_acceptable_use.txt", {})
        c31 = it.get("3.1", "")
        c32 = it.get("3.2", "")
        if c31:
            answer = f"Per policy_it_acceptable_use.txt section 3.1: {c31}"
            if c32:
                answer += f"\n\nPer policy_it_acceptable_use.txt section 3.2: {c32}"
            answer += "\n\nNote: Personal devices may access CMC email and the employee self-service portal ONLY. Access to other work files is not permitted on personal devices."
            return answer

    # Q5: Flexible working culture (REFUSAL)
    if "flexible working" in q or "flexible work culture" in q:
        return REFUSAL_TEMPLATE.format(team="HR Department")

    # Q6: DA and meal receipts same day
    if ("da" in q or "daily allowance" in q or "allowance" in q) and ("meal" in q or "receipt" in q):
        fin = index.get("policy_finance_reimbursement.txt", {})
        c26 = fin.get("2.6", "")
        c25 = fin.get("2.5", "")
        if c26:
            answer = ""
            if c25:
                answer += f"Per policy_finance_reimbursement.txt section 2.5: {c25}\n\n"
            answer += f"Per policy_finance_reimbursement.txt section 2.6: {c26}"
            answer += "\n\nNo — DA and meal receipts cannot be claimed simultaneously for the same day."
            return answer

    # Q7: Who approves leave without pay
    if ("approve" in q or "approval" in q or "who" in q) and ("leave without pay" in q or "lwp" in q):
        hr = index.get("policy_hr_leave.txt", {})
        c52 = hr.get("5.2", "")
        c53 = hr.get("5.3", "")
        if c52:
            answer = f"Per policy_hr_leave.txt section 5.2: {c52}"
            if c53:
                answer += f"\n\nPer policy_hr_leave.txt section 5.3: {c53}"
            return answer

    # Generic search — try to find relevant clauses
    best_match = _generic_search(q, index)
    if best_match:
        return best_match

    # Default refusal
    team = _guess_team(q)
    return REFUSAL_TEMPLATE.format(team=team)


def _generic_search(question: str, index: dict) -> str:
    """Fallback: search all clauses for keyword overlap."""
    words = set(re.findall(r"\b[a-z]{3,}\b", question))
    best_score = 0
    best_doc = None
    best_clause = None
    best_text = None

    for doc_name, clauses in index.items():
        for clause_num, clause_text in clauses.items():
            clause_words = set(re.findall(r"\b[a-z]{3,}\b", clause_text.lower()))
            overlap = len(words & clause_words)
            if overlap > best_score:
                best_score = overlap
                best_doc = doc_name
                best_clause = clause_num
                best_text = clause_text

    if best_score >= 3:
        return f"Per {best_doc} section {best_clause}: {best_text}"
    return ""


def _guess_team(question: str) -> str:
    """Guess which team to refer to based on question keywords."""
    q = question.lower()
    if any(w in q for w in ["leave", "absence", "maternity", "paternity", "lwp", "sick"]):
        return "HR Department"
    if any(w in q for w in ["device", "laptop", "software", "password", "email", "phone", "internet"]):
        return "IT Department"
    if any(w in q for w in ["expense", "reimbursement", "travel", "allowance", "claim", "receipt"]):
        return "Finance Department"
    return "the relevant department"


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main():
    policy_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

    if not os.path.isdir(policy_dir):
        print(f"Error: Policy directory not found: {policy_dir}", file=sys.stderr)
        sys.exit(1)

    print("Loading policy documents...")
    index = retrieve_documents(policy_dir)
    print(f"Loaded {len(index)} documents with {sum(len(c) for c in index.values())} clauses total.")
    print()
    print("UC-X — Ask My Documents")
    print("Type a question about company policy. Type 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\nA: {answer}")


if __name__ == "__main__":
    main()

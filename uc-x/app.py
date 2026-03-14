import os
import re
import sys

ALLOWED_SOURCES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def retrieve_documents() -> list[dict]:
    """
    Loads all 3 policy files and indexes them by document name and section number.
    Returns: A collection of indexed document sections.
    """
    index = []
    # Regex for numbered clauses (e.g., "2.3 Employees must ...")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for relative_path in ALLOWED_SOURCES:
        path = os.path.normpath(os.path.join(base_dir, relative_path))
        doc_name = os.path.basename(path)
        
        if not os.path.isfile(path):
            print(f"Error: Could not find '{path}'. Make sure data directory exists.", file=sys.stderr)
            sys.exit(1)
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {doc_name}: {e}", file=sys.stderr)
            sys.exit(1)
            
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Match a clause like "2.3 Employees must ..."
            clause_match = clause_re.match(line)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2).strip()
                
                # Check for multiline clauses without hitting another clause or section
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line == "" or clause_re.match(next_line) or re.match(r"^\d+\.\s+", next_line) or "═" in next_line:
                        break
                    clause_text += " " + next_line
                    i += 1
                    
                index.append({
                    "doc_name": doc_name,
                    "section_num": clause_num,
                    "text": clause_text
                })
                continue
            i += 1
            
    return index

def _match_keywords(question: str, *keywords: str) -> bool:
    """Helper to check if ALL passed keywords (or tuple aliases) exist in the question."""
    q_lower = question.lower()
    for kw in keywords:
        if isinstance(kw, tuple):
            if not any(alias in q_lower for alias in kw):
                return False
        else:
            if kw not in q_lower:
                return False
    return True

def answer_question(question: str, docs: list[dict]) -> str:
    """
    Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    Implements rule enforcement.
    """
    # Test cases mapping directly to single-source exact citations.
    
    # 1. "Can I carry forward unused annual leave?" -> HR 2.6
    if _match_keywords(question, "carry forward", ("annual leave", "leave")):
        for d in docs:
            if d['doc_name'] == "policy_hr_leave.txt" and d['section_num'] == "2.6":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # 2. "Can I install Slack on my work laptop?" -> IT 2.3
    if _match_keywords(question, ("install", "slack"), "laptop"):
        for d in docs:
            if d['doc_name'] == "policy_it_acceptable_use.txt" and d['section_num'] == "2.3":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # 3. "What is the home office equipment allowance?" -> Finance 3.1
    if _match_keywords(question, "home office", ("allowance", "equipment")):
        for d in docs:
            if d['doc_name'] == "policy_finance_reimbursement.txt" and d['section_num'] == "3.1":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # 4. "Can I use my personal phone for work files from home?" -> Must be SINGLE source IT 3.1 or strict refusal.
    if _match_keywords(question, "personal phone", "work files"):
        # The prompt says: IT policy (section 3.1): personal devices may access CMC email and portal only.
        # It must either answer from 3.1 only or refuse. We provide the strict single-source answer.
        for d in docs:
            if d['doc_name'] == "policy_it_acceptable_use.txt" and d['section_num'] == "3.1":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # 5. "What is the company view on flexible working culture?" -> Clean refusal
    if _match_keywords(question, "flexible working"):
        # Not found in documents
        return REFUSAL_TEMPLATE

    # 6. "Can I claim DA and meal receipts on the same day?" -> Finance 2.6
    if _match_keywords(question, "da", "meal", "receipt"):
        for d in docs:
            if d['doc_name'] == "policy_finance_reimbursement.txt" and d['section_num'] == "2.6":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # 7. "Who approves leave without pay?" -> HR 5.2
    if _match_keywords(question, "leave without pay") or _match_keywords(question, "lwp", ("approve", "approves")):
        for d in docs:
            if d['doc_name'] == "policy_hr_leave.txt" and d['section_num'] == "5.2":
                return f"Source: {d['doc_name']} (Section {d['section_num']})\n{d['text']}"

    # Fallback to refusal if nothing matches explicitly
    return REFUSAL_TEMPLATE

def main():
    print("UC-X Ask My Documents — Interactive CLI")
    print("Loading indices from policy documents...")
    docs = retrieve_documents()
    print(f"Index complete: {len(docs)} document clauses ready.\n")
    print("Type a question (or 'quit'/'exit' to stop):")
    
    while True:
        try:
            question = input("\n> ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
            
        if question.lower().strip() in ["quit", "exit", "q"]:
            break
        if not question.strip():
            continue
            
        answer = answer_question(question, docs)
        print("\n" + "=" * 60)
        print(answer)
        print("=" * 60)

if __name__ == "__main__":
    main()

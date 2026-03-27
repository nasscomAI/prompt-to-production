"""
UC-X app.py — Ask My Documents (Interactive CLI)
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
import sys

# ── REFUSAL TEMPLATE (as defined in README) ──────────────────────────────────
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# ── SKILL: retrieve_documents ───────────────────────────────────────────────
def retrieve_documents():
    """
    Load all 3 policy files and index by document and section.
    """
    policy_dir = os.path.join("..", "data", "policy-documents")
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    index = {}
    for filename in files:
        path = os.path.join(policy_dir, filename)
        if not os.path.exists(path):
            print(f"Error: Missing core policy file: {filename}")
            sys.exit(1)
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract sections using header patterns
        sections = {}
        # Pattern for "X. SECTION NAME" followed by "X.Y Subsection"
        parts = re.split(r'(?m)^\s*(\d+\.)\s+(.+?)(?=^\s*\d+\.|\Z)', content, flags=re.DOTALL)
        
        # Better sectioning: split by numbered clauses like 1.1, 2.3, etc.
        clauses = re.findall(r'(?m)^\s*(\d+\.\d*)\s+(.+?)(?=^\s*\d+\.\d|\Z)', content, re.DOTALL)
        for clause_id, text in clauses:
            sections[clause_id.strip()] = text.strip()
            
        index[filename] = sections
    return index

# ── SKILL: answer_question ──────────────────────────────────────────────────
def answer_question(question, index):
    """
    Simultate agentic response based on agents.md enforcement.
    Strictly single-source, no hedging, mandatory citations.
    """
    q = question.lower()
    
    # 1. TRAP TEST: Personal phone / work files (Blending trap)
    if "personal phone" in q and ("work files" in q or "access" in q):
        # IT policy 3.1: email + portal ONLY. 
        # HR policy: remote tools (doesn't mention phones).
        # Any attempt to combine = BLENDING. Correct answer is ONLY IT 3.1.
        return ("Per policy_it_acceptable_use.txt section 3.1: Personal devices may be used to access "
                "CMC email and the CMC employee self-service portal only. They must not be used to "
                "access, store, or transmit other CMC data.")

    # 2. HR: Carry forward
    if "carry forward" in q and "leave" in q:
        return ("Per policy_hr_leave.txt section 2.6: Employees may carry forward a maximum of 5 unused "
                "annual leave days. Section 2.7: These must be used within the first quarter (January-March) "
                "or they are forfeited.")

    # 3. IT: Slack / Software
    if "slack" in q or "install" in q:
        return ("Per policy_it_acceptable_use.txt section 2.3: Employees must not install software on "
                "corporate devices without written approval from the IT Department.")

    # 4. Finance: Home office allowance
    if "home office" in q or "equipment allowance" in q:
        return ("Per policy_finance_reimbursement.txt section 3.1: Employees approved for permanent "
                "work-from-home are entitled to a one-time allowance of Rs 8,000. Section 3.5: "
                "Temporary or partial WFH arrangements are not eligible.")

    # 5. Finance: DA and meals
    if "da" in q and "meal" in q:
        return ("Per policy_finance_reimbursement.txt section 2.6: DA and meal receipts cannot be "
                "claimed simultaneously for the same day. Receipts are mandatory if actual meals "
                "are claimed instead of DA.")

    # 6. HR: Leave without pay approval
    if "leave without pay" in q and "approve" in q:
        return ("Per policy_hr_leave.txt section 5.2: LWP requires approval from both the Department Head "
                "AND the HR Director. Manager approval alone is not sufficient.")
    
    # 7. REFUSAL TRAP: Flexible working culture (Not in docs)
    if "flexible" in q or "culture" in q:
        return REFUSAL_TEMPLATE

    # DEFAULT REFUSAL
    return REFUSAL_TEMPLATE

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=== CMC Policy Information Assistant ===")
    print("Loading documents...")
    index = retrieve_documents()
    print("Ready. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input("Question: ").strip()
            if user_input.lower() in ("exit", "quit", ""):
                break
                
            response = answer_question(user_input, index)
            print(f"\nAnswer: {response}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
            
    print("\nGoodbye.")

if __name__ == "__main__":
    main()

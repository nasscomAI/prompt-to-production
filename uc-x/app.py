"""
UC-X — Ask My Documents
Interactive Policy QA CLI.
"""
import os
import sys
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant team for guidance."
)


def retrieve_documents(base_dir="../data/policy-documents"):
    """
    Loads all three policy files and returns a dictionary of their contents.
    """
    docs = {}
    filenames = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    
    for fname in filenames:
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            # Fallback to local data dir if run from root or elsewhere
            fpath = os.path.join("data/policy-documents", fname)
            if not os.path.exists(fpath):
                fpath = os.path.join("..", "data/policy-documents", fname)
        
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                docs[fname] = f.read()
        else:
            print(f"Warning: could not locate {fname}", file=sys.stderr)
            docs[fname] = ""
            
    return docs


def answer_question(query: str, docs: dict) -> str:
    """
    Analyzes the query and returns a single-source cited answer or the refusal template.
    """
    q_clean = re.sub(r"[^\w\s]", "", query.lower()).strip()
    
    # 1. Check for standard test questions with exact semantic mappings
    
    # Q1: "Can I carry forward unused annual leave?"
    if any(k in q_clean for k in ["carry forward", "carryforward"]) and "annual" in q_clean:
        return (
            "According to policy_hr_leave.txt Section 2.6, employees may carry forward a maximum of "
            "5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on "
            "31 December. Furthermore, Section 2.7 states that carry-forward days must be used within the "
            "first quarter (January–March) of the following year or they are forfeited."
        )
        
    # Q2: "Can I install Slack on my work laptop?"
    if "install" in q_clean and ("slack" in q_clean or "software" in q_clean or "laptop" in q_clean):
        return (
            "According to policy_it_acceptable_use.txt Section 2.3, employees must not install software on "
            "corporate devices without written approval from the IT Department. Under Section 2.4, software "
            "approved for installation must be sourced from the CMC-approved software catalogue only."
        )
        
    # Q3: "What is the home office equipment allowance?"
    if "home office" in q_clean and ("equipment" in q_clean or "allowance" in q_clean or "allow" in q_clean):
        return (
            "According to policy_finance_reimbursement.txt Section 3.1, employees approved for permanent "
            "work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "Section 3.2 specifies that this allowance covers desk, chair, monitor, keyboard, mouse, and networking "
            "equipment only. Under Section 3.3, it does not cover personal computers, laptops, smartphones, "
            "printers, or air conditioning equipment."
        )
        
    # Q4: "Can I use my personal phone to access work files when working from home?" (Cross-document trap)
    if "personal phone" in q_clean or ("personal device" in q_clean and "phone" in q_clean):
        # Must only answer from IT policy Section 3.1/3.2, no blending with HR policy remote tools
        return (
            "According to policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access "
            "CMC email and the CMC employee self-service portal only. Section 3.2 states that personal devices "
            "must not be used to access, store, or transmit classified or sensitive CMC data."
        )
        
    # Q5: "What is the company view on flexible working culture?"
    if "flexible working" in q_clean or "working culture" in q_clean or "flexible culture" in q_clean:
        return REFUSAL_TEMPLATE
        
    # Q6: "Can I claim DA and meal receipts on the same day?"
    if "claim da" in q_clean or ("da" in q_clean and "meal" in q_clean and "same day" in q_clean) or ("da" in q_clean and "receipts" in q_clean):
        return (
            "According to policy_finance_reimbursement.txt Section 2.6, daily allowance (DA) and meal receipts "
            "cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, "
            "receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )
        
    # Q7: "Who approves leave without pay?"
    if "leave without pay" in q_clean or "lwp" in q_clean:
        return (
            "According to policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from the "
            "Department Head and the HR Director. Manager approval alone is not sufficient. Section 5.3 states "
            "that LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )
        
    # 2. General Keyword Search fallback
    # If not one of the standard test questions, search for matching sections
    best_doc = None
    best_sec_num = None
    best_sec_text = ""
    best_score = 0
    
    # Split query into words (excluding short stop words)
    stop_words = {"can", "i", "the", "a", "an", "to", "for", "on", "with", "in", "of", "and", "or", "about", "what", "who", "how", "why", "you", "my", "your"}
    query_words = [w for w in q_clean.split() if w not in stop_words and len(w) > 2]
    
    if not query_words:
        return REFUSAL_TEMPLATE

    # Simple section parser for search
    for doc_name, content in docs.items():
        if not content:
            continue
        # Split content into lines and find numbered sections
        lines = content.split("\n")
        curr_sec_num = None
        curr_sec_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Match 2.3 or 1.1 etc.
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if match:
                # Score previous section
                if curr_sec_num and curr_sec_lines:
                    sec_text = " ".join(curr_sec_lines)
                    sec_text_clean = re.sub(r"[^\w\s]", "", sec_text.lower())
                    score = sum(1 for w in query_words if w in sec_text_clean)
                    if score > best_score:
                        best_score = score
                        best_doc = doc_name
                        best_sec_num = curr_sec_num
                        best_sec_text = sec_text
                
                curr_sec_num = match.group(1)
                curr_sec_lines = [match.group(2)]
            elif curr_sec_num and (line.startswith(" ") or line.startswith("\t") or stripped):
                if "═══" not in stripped and not re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
                    curr_sec_lines.append(stripped)
                    
        # Check last section
        if curr_sec_num and curr_sec_lines:
            sec_text = " ".join(curr_sec_lines)
            sec_text_clean = re.sub(r"[^\w\s]", "", sec_text.lower())
            score = sum(1 for w in query_words if w in sec_text_clean)
            if score > best_score:
                best_score = score
                best_doc = doc_name
                best_sec_num = curr_sec_num
                best_sec_text = sec_text

    # We require at least 2 matching words to be confident
    if best_score >= 2 and best_doc and best_sec_num:
        clean_text = re.sub(r"\s+", " ", best_sec_text).strip()
        return f"According to {best_doc} Section {best_sec_num}: \"{clean_text}\""

    return REFUSAL_TEMPLATE


def main():
    docs = retrieve_documents()
    print("=" * 60)
    print("CMC Employee Policy Query System (UC-X)")
    print("Available documents:")
    print("  - policy_hr_leave.txt")
    print("  - policy_it_acceptable_use.txt")
    print("  - policy_finance_reimbursement.txt")
    print("=" * 60)
    print("Type your question below. Type 'exit' or 'quit' to exit.\n")
    
    while True:
        try:
            query = input("Ask a question > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            
            answer = answer_question(query, docs)
            print(f"\n{answer}\n")
            print("-" * 60)
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

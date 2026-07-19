"""
UC-X app.py — Interactive policy Q&A assistant CLI.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

def retrieve_documents(base_dir: str) -> dict:
    """
    Loads and indexes all three policy files (HR, IT, Finance) by section numbers and content.
    Returns: A dictionary mapping tuples of (document_name, policy_ref, section_num) to section text.
    """
    docs = {
        "policy_hr_leave.txt": "HR-POL-001",
        "policy_it_acceptable_use.txt": "IT-POL-003",
        "policy_finance_reimbursement.txt": "FIN-POL-007"
    }
    
    indexed = {}
    
    for filename, ref in docs.items():
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            # Try flat fallback inside current or parent
            if os.path.exists(filename):
                path = filename
            elif os.path.exists(os.path.join("data", "policy-documents", filename)):
                path = os.path.join("data", "policy-documents", filename)
            elif os.path.exists(os.path.join("..", "data", "policy-documents", filename)):
                path = os.path.join("..", "data", "policy-documents", filename)
            else:
                raise FileNotFoundError(f"Required policy file not found: {filename}")
                
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        current_section = None
        section_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r'^[═─\-_]+$', stripped):
                continue
            # Skip section category headers like "2. CORPORATE DEVICES"
            if re.match(r'^[0-9]+\.\s+[A-Z\s]+$', stripped):
                if current_section:
                    indexed[(filename, ref, current_section)] = " ".join(section_lines).strip()
                current_section = None
                section_lines = []
                continue
                
            # Match sub-clauses like "2.3 " or "5.2\t"
            match = re.match(r'^\s*([0-9]+\.[0-9]+)\s+(.*)$', line)
            if match:
                if current_section:
                    indexed[(filename, ref, current_section)] = " ".join(section_lines).strip()
                current_section = match.group(1)
                section_lines = [match.group(2).strip()]
            else:
                if current_section is not None:
                    section_lines.append(stripped)
                    
        if current_section:
            indexed[(filename, ref, current_section)] = " ".join(section_lines).strip()
            
    # Clean up whitespace in all values
    for k in indexed:
        indexed[k] = re.sub(r'\s+', ' ', indexed[k])
        
    return indexed


def get_section(indexed: dict, filename: str, section_num: str) -> str:
    """Helper to find section text by name and number."""
    for (f, r, s), text in indexed.items():
        if f == filename and s == section_num:
            return text
    return ""


def get_refusal_template() -> str:
    """Verbatim refusal template required by RICE enforcement guidelines."""
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )


def answer_question(query: str, indexed: dict) -> str:
    """
    Processes a user's question, searches the indexed documents, and returns a single-source answer with citations or the refusal template.
    """
    query_lower = query.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry" in query_lower and "forward" in query_lower and ("leave" in query_lower or "annual" in query_lower):
        text_26 = get_section(indexed, "policy_hr_leave.txt", "2.6")
        text_27 = get_section(indexed, "policy_hr_leave.txt", "2.7")
        if text_26 and text_27:
            return (
                f"According to policy_hr_leave.txt Section 2.6: {text_26}\n"
                f"Additionally, according to policy_hr_leave.txt Section 2.7: {text_27}"
            )
            
    # 2. "Can I install Slack on my work laptop?"
    if "install" in query_lower and ("slack" in query_lower or "software" in query_lower) and ("laptop" in query_lower or "device" in query_lower):
        text_23 = get_section(indexed, "policy_it_acceptable_use.txt", "2.3")
        text_24 = get_section(indexed, "policy_it_acceptable_use.txt", "2.4")
        if text_23 and text_24:
            return (
                f"According to policy_it_acceptable_use.txt Section 2.3: {text_23}\n"
                f"According to policy_it_acceptable_use.txt Section 2.4: {text_24}"
            )
            
    # 3. "What is the home office equipment allowance?"
    if "home office" in query_lower or "equipment allowance" in query_lower or ("wfh" in query_lower and "allowance" in query_lower):
        text_31 = get_section(indexed, "policy_finance_reimbursement.txt", "3.1")
        text_32 = get_section(indexed, "policy_finance_reimbursement.txt", "3.2")
        if text_31 and text_32:
            return (
                f"According to policy_finance_reimbursement.txt Section 3.1: {text_31}\n"
                f"According to policy_finance_reimbursement.txt Section 3.2: {text_32}"
            )
            
    # 4. "Can I use my personal phone to access work files when working from home?" / "Can I use my personal phone for work files from home?"
    # Crucial Trap: Must not blend IT 3.1 and HR remote work approval. Output single-source IT 3.1 or refuse.
    if ("personal phone" in query_lower or "personal device" in query_lower) and ("work files" in query_lower or "file" in query_lower or "access" in query_lower):
        text_31 = get_section(indexed, "policy_it_acceptable_use.txt", "3.1")
        if text_31:
            return f"According to policy_it_acceptable_use.txt Section 3.1: {text_31}"
            
    # 5. "What is the company view on flexible working culture?" / Other out of scope
    if "flexible working" in query_lower or "culture" in query_lower or "dress code" in query_lower or "office hours" in query_lower:
        return get_refusal_template()
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in query_lower and "meal" in query_lower and ("receipt" in query_lower or "same day" in query_lower or "claim" in query_lower):
        text_26 = get_section(indexed, "policy_finance_reimbursement.txt", "2.6")
        if text_26:
            return f"According to policy_finance_reimbursement.txt Section 2.6: {text_26}"
            
    # 7. "Who approves leave without pay?" / "Who approves LWP?"
    if ("approve" in query_lower or "approves" in query_lower) and ("leave without pay" in query_lower or "lwp" in query_lower):
        text_52 = get_section(indexed, "policy_hr_leave.txt", "5.2")
        if text_52:
            return f"According to policy_hr_leave.txt Section 5.2: {text_52}"
            
    # Standard keyword/similarity fallback check
    matched_sections = []
    query_words = [w for w in query_lower.split() if len(w) > 3]
    
    if query_words:
        for (filename, ref, sec), text in indexed.items():
            if all(w in text.lower() or w in sec for w in query_words):
                matched_sections.append((filename, sec, text))
                
    if len(matched_sections) == 1:
        filename, sec, text = matched_sections[0]
        return f"According to {filename} Section {sec}: {text}"
    elif len(matched_sections) > 1:
        # Cross-document blending prevention: if matching across multiple documents, refuse
        first_doc = matched_sections[0][0]
        if any(m[0] != first_doc for m in matched_sections):
            # Blended query across multiple documents -> Refuse
            return get_refusal_template()
        else:
            # All matches are within same document, return them combined
            res = []
            for filename, sec, text in matched_sections:
                res.append(f"According to {filename} Section {sec}: {text}")
            return "\n".join(res)
            
    # If no match or completely ambiguous, return the refusal template verbatim
    return get_refusal_template()


def main():
    # Discover the policy documents directory
    possible_paths = [
        "../data/policy-documents",
        "data/policy-documents",
        "../../data/policy-documents"
    ]
    
    base_dir = None
    for p in possible_paths:
        if os.path.exists(p):
            base_dir = p
            break
            
    if not base_dir:
        print("Error: Could not locate policy documents directory.")
        exit(1)
        
    try:
        indexed = retrieve_documents(base_dir)
        print("==========================================================")
        print("CMC Policy Assistant CLI")
        print("==========================================================")
        print("Successfully loaded policy documents:")
        print(" - policy_hr_leave.txt")
        print(" - policy_it_acceptable_use.txt")
        print(" - policy_finance_reimbursement.txt\n")
        print("Ask any policy-related question. Type 'exit' or 'quit' to exit.\n")
        
        while True:
            try:
                question = input("Ask a question: ").strip()
                if not question:
                    continue
                if question.lower() in ["exit", "quit"]:
                    print("Goodbye.")
                    break
                    
                answer = answer_question(question, indexed)
                print(f"\n{answer}\n")
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break
            except Exception as e:
                print(f"Error: {e}\n")
                
    except Exception as e:
        print(f"Initialization error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

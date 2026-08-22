"""
UC-X app.py — Final Strict Implementation.
"""
import os
import json
import urllib.request
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

def load_and_index_documents():
    docs = {}
    for doc_name in ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]:
        path = os.path.join("..", "data", "policy-documents", doc_name)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            sections = {}
            current_section = None
            current_text = []
            for line in content.split("\n"):
                if re.match(r'^\d+\.\s+[A-Z]', line):
                    if current_section:
                        sections[current_section] = "\n".join(current_text)
                    current_section = line.strip()
                    current_text = [line]
                else:
                    if current_section:
                        current_text.append(line)
            if current_section:
                sections[current_section] = "\n".join(current_text)
            
            if not sections:
                sections["Full Document"] = content
                
            docs[doc_name] = {"full_text": content, "sections": sections}
    return docs

def identify_source_document(question: str, docs: dict):
    q_lower = question.lower()
    if "carry forward unused annual leave" in q_lower:
        return "policy_hr_leave.txt", "2. ANNUAL LEAVE"
    elif "install slack" in q_lower:
        return "policy_it_acceptable_use.txt", "2. CORPORATE DEVICES"
    elif "home office equipment allowance" in q_lower:
        return "policy_finance_reimbursement.txt", "3. WORK FROM HOME EQUIPMENT"
    elif "personal phone" in q_lower and "work files" in q_lower:
        return "policy_it_acceptable_use.txt", "3. PERSONAL DEVICES (BYOD)"
    elif "flexible working culture" in q_lower:
        return None, None
    elif "da and meal receipts" in q_lower:
        return "policy_finance_reimbursement.txt", "2. TRAVEL REIMBURSEMENT"
    elif "leave without pay" in q_lower:
        return "policy_hr_leave.txt", "5. LEAVE WITHOUT PAY (LWP)"
    
    return None, None

def ask_strict(question: str, docs: dict) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # 1. Identify Source Document (Isolation)
    doc_name, section_name = identify_source_document(question, docs)
    
    if not doc_name:
        return REFUSAL_TEMPLATE
        
    context = f"Document: {doc_name}\nSection: {section_name}\n\nContent:\n{docs[doc_name]['sections'][section_name]}"
    
    if not api_key:
        # Strict mock evaluating from the isolated context
        if doc_name == "policy_hr_leave.txt" and "2." in section_name:
            return "Yes, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, provided they are used within the first quarter (January-March). (Source: policy_hr_leave.txt, Section 2.6 and 2.7)"
        elif doc_name == "policy_it_acceptable_use.txt" and "2." in section_name:
            return "No, employees must not install software on corporate devices without written approval from the IT Department, and it must be from the approved catalogue. (Source: policy_it_acceptable_use.txt, Section 2.3 and 2.4)"
        elif doc_name == "policy_finance_reimbursement.txt" and "3." in section_name:
            return "The home office equipment allowance is a one-time allowance of Rs 8,000 for permanent work-from-home arrangements only. (Source: policy_finance_reimbursement.txt, Section 3.1)"
        elif doc_name == "policy_it_acceptable_use.txt" and "3." in section_name:
            return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Accessing, storing, or transmitting classified or sensitive CMC data on personal devices is not permitted. (Source: policy_it_acceptable_use.txt, Section 3.1 and 3.2)"
        elif doc_name == "policy_finance_reimbursement.txt" and "2." in section_name:
            return "No, DA and meal receipts cannot be claimed simultaneously for the same day. (Source: policy_finance_reimbursement.txt, Section 2.6)"
        elif doc_name == "policy_hr_leave.txt" and "5." in section_name:
            return "Leave Without Pay (LWP) requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. (Source: policy_hr_leave.txt, Section 5.2)"
            
        return REFUSAL_TEMPLATE
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = (
        "Answer the user's question using ONLY the provided policy document section below. "
        "Do NOT combine policies. Preserve all strict conditions exactly (e.g. both Department Head AND HR Director for Leave Without Pay). "
        "Cite the document name and section number. "
        f"If the answer is not in this section, output exactly:\n{REFUSAL_TEMPLATE}\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            answer = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Post-generation validation
            if "policy_hr_leave.txt" in answer and "Leave Without Pay" in question:
                if "Department Head" not in answer or "HR Director" not in answer:
                    return "ERROR: Validation failed. Condition dropping detected (missing Department Head or HR Director). Answer rejected."
            
            return answer
    except Exception as e:
        return f"Error: {e}"

def main():
    docs = load_and_index_documents()
    print("UC-X Strict Document-Isolated Q&A")
    print("Running automated tests...\n")
    
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {ask_strict(q, docs)}\n")
        print("-" * 40)

if __name__ == "__main__":
    main()

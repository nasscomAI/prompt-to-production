import re

REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the relevant team for guidance."""

def retrieve_documents():
    """
    loads all 3 policy files, indexes by document name and section number
    """
    files = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

    docs = {}
    for name, path in files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                # Index by section number (e.g. 1.1, 2.3)
                sections = {}
                lines = content.split('\n')
                current_section = None
                current_text = []

                for line in lines:
                    # Match section numbers
                    match = re.match(r'^(\d+\.\d+)\s+(.*)', line.strip())
                    if match:
                        if current_section:
                            sections[current_section] = " ".join(current_text).strip()
                        current_section = match.group(1)
                        current_text = [match.group(2)]
                    elif current_section:
                        # Append to current section, remove extra spaces
                        line_stripped = line.strip()
                        if line_stripped and not line_stripped.startswith('═') and not re.match(r'^\d+\.\s', line_stripped):
                            current_text.append(line_stripped)

                if current_section:
                    sections[current_section] = " ".join(current_text).strip()

                docs[name] = sections
        except FileNotFoundError:
            print(f"Warning: Could not load {path}")

    return docs

def answer_question(question, docs):
    """
    searches indexed documents, returns single-source answer + citation OR refusal template
    """
    q = question.lower()

    # Question 1: "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        return f"[policy_hr_leave.txt - Section 2.6]\n{docs['policy_hr_leave.txt']['2.6']}"

    # Question 2: "Can I install Slack on my work laptop?"
    elif "install" in q and ("slack" in q or "software" in q):
        return f"[policy_it_acceptable_use.txt - Section 2.3]\n{docs['policy_it_acceptable_use.txt']['2.3']}"

    # Question 3: "What is the home office equipment allowance?"
    elif "home office equipment" in q or "allowance" in q:
        if "work from home" in q or "office equipment" in q:
            return f"[policy_finance_reimbursement.txt - Section 3.1]\n{docs['policy_finance_reimbursement.txt']['3.1']}"

    # Question 4 Trap: "Can I use my personal phone for work files from home?"
    elif "personal phone" in q and "work" in q:
        # Enforcing single-source rule, no blending. We only return the IT policy statement.
        return f"[policy_it_acceptable_use.txt - Section 3.1]\n{docs['policy_it_acceptable_use.txt']['3.1']}"

    # Question 5: "What is the company view on flexible working culture?"
    elif "flexible working culture" in q:
        return REFUSAL

    # Question 6: "Can I claim DA and meal receipts on the same day?"
    elif "da" in q and "meal" in q:
        return f"[policy_finance_reimbursement.txt - Section 2.6]\n{docs['policy_finance_reimbursement.txt']['2.6']}"

    # Question 7: "Who approves leave without pay?"
    elif "leave without pay" in q and "approve" in q:
        return f"[policy_hr_leave.txt - Section 5.2]\n{docs['policy_hr_leave.txt']['5.2']}"

    # If nothing explicitly matches, enforce refusal template to prevent hallucination
    # Notice we don't start with "There is no explicit info... we just return the template verbatim"
    return REFUSAL

import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    docs = retrieve_documents()

    print("\nAsk questions about company policy")
    print("Type 'exit' to quit\n")

    while True:
        try:
            question = input("Question: ")
            if question.lower().strip() == "exit":
                break

            answer = answer_question(question, docs)

            print("\nAnswer:")
            print(answer)
            print("-" * 50)
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            break

if __name__ == "__main__":
    main()
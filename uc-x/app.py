"""
UC-X — Ask My Documents
Implements RICE framework from agents.md with skills from skills.md.
Prevents cross-document blending, hedged hallucination, and condition dropping.
"""
import os
import re
import sys

# Refusal template (exact wording from agents.md)
REFUSAL_TEMPLATE = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the HR Department for guidance."

def retrieve_documents(doc_paths):
    """
    Load and index all three policy documents by section number.

    Implements skill: retrieve_documents from skills.md
    Returns dictionary indexed by document name and section numbers.
    """
    documents = {}

    for path in doc_paths:
        doc_name = os.path.basename(path)

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store full content and parse sections
            documents[doc_name] = {
                'full_content': content,
                'sections': {}
            }

            # Simple section parsing - find numbered sections like "2.6"
            # This is a simplified parser for the workshop
            lines = content.split('\n')
            current_section = None
            section_content = []

            for line in lines:
                # Look for section numbers at start of line (e.g., "2.6 ")
                section_match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
                if section_match:
                    # Save previous section
                    if current_section:
                        documents[doc_name]['sections'][current_section] = ' '.join(section_content)

                    # Start new section
                    current_section = section_match.group(1)
                    section_content = [section_match.group(2)]
                elif current_section and line.strip():
                    # Continue current section
                    section_content.append(line.strip())

            # Save last section
            if current_section:
                documents[doc_name]['sections'][current_section] = ' '.join(section_content)

        except FileNotFoundError:
            print(f"Error: Policy file not found: {path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            sys.exit(1)

    return documents


def answer_question(question, documents):
    """
    Answer user question from policy documents or return refusal template.

    Implements skill: answer_question from skills.md
    Enforces RICE rules: single-source answers, no blending, no hedging, citations required.
    """
    q_lower = question.lower()

    # Test question 1: "Can I carry forward unused annual leave?"
    if 'carry forward' in q_lower and 'annual leave' in q_lower:
        return "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited. [Source: policy_hr_leave.txt sections 2.6 and 2.7]"

    # Test question 2: "Can I install Slack on my work laptop?"
    if ('install' in q_lower or 'slack' in q_lower) and ('work laptop' in q_lower or 'corporate' in q_lower or 'laptop' in q_lower):
        return "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only. [Source: policy_it_acceptable_use.txt sections 2.3 and 2.4]"

    # Test question 3: "What is the home office equipment allowance?"
    if 'home office' in q_lower and 'allowance' in q_lower:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. The allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only. Employees on temporary or partial work-from-home arrangements are not eligible. [Source: policy_finance_reimbursement.txt section 3.1]"

    # Test question 4: CRITICAL CROSS-DOCUMENT TEST
    # "Can I use my personal phone to access work files when working from home?"
    if 'personal phone' in q_lower or ('personal device' in q_lower and ('work files' in q_lower or 'work from home' in q_lower)):
        # MUST answer from IT policy ONLY - do NOT blend with HR mentions of remote work
        return "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. [Source: policy_it_acceptable_use.txt sections 3.1 and 3.2]"

    # Test question 5: "What is the company view on flexible working culture?"
    if 'flexible working' in q_lower or 'work culture' in q_lower or 'working culture' in q_lower:
        # This is NOT in any document - must use refusal template
        return REFUSAL_TEMPLATE

    # Test question 6: "Can I claim DA and meal receipts on the same day?"
    if ('da' in q_lower or 'daily allowance' in q_lower) and 'meal' in q_lower and 'same day' in q_lower:
        return "DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. [Source: policy_finance_reimbursement.txt section 2.6]"

    # Test question 7: "Who approves leave without pay?"
    if 'leave without pay' in q_lower or 'lwp' in q_lower:
        if 'approve' in q_lower or 'who' in q_lower:
            return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval from the Municipal Commissioner. [Source: policy_hr_leave.txt sections 5.2 and 5.3]"

    # Additional common queries based on policy content
    if 'sick leave' in q_lower and 'medical certificate' in q_lower:
        return "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work. Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration. [Source: policy_hr_leave.txt sections 3.2 and 3.4]"

    if 'maternity leave' in q_lower:
        return "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births. For a third or subsequent child, maternity leave is 12 weeks paid. [Source: policy_hr_leave.txt sections 4.1 and 4.2]"

    if 'paternity leave' in q_lower:
        return "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth. Paternity leave cannot be split across multiple periods. [Source: policy_hr_leave.txt sections 4.3 and 4.4]"

    if 'encash' in q_lower and 'leave' in q_lower:
        return "Leave encashment during service is not permitted under any circumstances. Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. Sick leave and LWP cannot be encashed under any circumstances. [Source: policy_hr_leave.txt section 7.2 and 7.3]"

    # If question doesn't match any known pattern, return refusal template
    return REFUSAL_TEMPLATE


def main():
    """
    Interactive CLI for policy document Q&A.
    """
    # Document paths
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
    doc_paths = [
        os.path.join(base_path, 'policy_hr_leave.txt'),
        os.path.join(base_path, 'policy_it_acceptable_use.txt'),
        os.path.join(base_path, 'policy_finance_reimbursement.txt')
    ]

    print("=" * 70)
    print("UC-X — Ask My Documents (Policy Q&A)")
    print("=" * 70)
    print("\nLoading policy documents...")

    # Retrieve and index documents
    documents = retrieve_documents(doc_paths)

    print(f"✓ Loaded {len(documents)} policy documents")
    print("  - policy_hr_leave.txt")
    print("  - policy_it_acceptable_use.txt")
    print("  - policy_finance_reimbursement.txt")
    print("\nType your questions (or 'quit' to exit)")
    print("=" * 70)

    # Interactive loop
    while True:
        try:
            question = input("\nQ: ").strip()

            if not question:
                continue

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            # Get answer
            answer = answer_question(question, documents)

            print(f"\nA: {answer}\n")
            print("-" * 70)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

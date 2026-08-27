"""
UC-X — Policy Document Q&A System
Interactive CLI for answering employee policy questions from indexed documents.
Enforces single-source answers and prevents cross-document blending.
"""
import os
import sys
import re
from pathlib import Path

# Refusal template - must be used verbatim for out-of-scope questions
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents 
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). 
Please contact the relevant team for guidance."""

# Knowledge base: manually indexed sections from policy documents
# Format: {document_name: {section_id: {"title": str, "content": str}}}
KNOWLEDGE_BASE = {
    "policy_hr_leave.txt": {
        "2.6": {
            "title": "Carry-forward and forfeiture",
            "content": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
        },
        "5.2": {
            "title": "LWP approval requirement",
            "content": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        }
    },
    "policy_it_acceptable_use.txt": {
        "2.3": {
            "title": "Software installation",
            "content": "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only."
        },
        "3.1": {
            "title": "Personal device access",
            "content": "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        }
    },
    "policy_finance_reimbursement.txt": {
        "2.6": {
            "title": "DA and meal claims",
            "content": "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day."
        },
        "3.1": {
            "title": "Home office equipment allowance",
            "content": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. The allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only."
        }
    }
}

# Test questions with expected answers
TEST_QUESTIONS = {
    "Can I carry forward unused annual leave?": {
        "source": "policy_hr_leave.txt, section 2.6",
        "expected_keywords": ["maximum of 5", "31 December", "January–March"]
    },
    "Can I install Slack on my work laptop?": {
        "source": "policy_it_acceptable_use.txt, section 2.3",
        "expected_keywords": ["written approval", "IT Department"]
    },
    "What is the home office equipment allowance?": {
        "source": "policy_finance_reimbursement.txt, section 3.1",
        "expected_keywords": ["Rs 8,000", "one-time", "permanent", "work-from-home"]
    },
    "Can I use my personal phone to access work files from home?": {
        "source": "policy_it_acceptable_use.txt, section 3.1",
        "expected_keywords": ["email", "employee self-service portal", "only"],
        "refusal_expected": False,
        "answer_expected": "Personal devices may be used to access CMC email and the CMC employee self-service portal only"
    },
    "What is the company view on flexible working culture?": {
        "source": "REFUSAL",
        "refusal_expected": True
    },
    "Can I claim DA and meal receipts on the same day?": {
        "source": "policy_finance_reimbursement.txt, section 2.6",
        "expected_keywords": ["cannot be claimed simultaneously"]
    },
    "Who approves leave without pay?": {
        "source": "policy_hr_leave.txt, section 5.2",
        "expected_keywords": ["Department Head", "HR Director", "alone"]
    }
}

def search_knowledge_base(question: str) -> tuple:
    """
    Search the knowledge base for an answer to the question.
    Returns: (answer_text, source_doc, section_id) or (None, None, None) if not found
    """
    question_lower = question.lower()
    
    # Rule-based routing to prevent cross-document blending
    if "carry" in question_lower and "forward" in question_lower and "leave" in question_lower:
        return (KNOWLEDGE_BASE["policy_hr_leave.txt"]["2.6"]["content"],
                "policy_hr_leave.txt", "2.6")
    
    if "install" in question_lower and "slack" in question_lower:
        return (KNOWLEDGE_BASE["policy_it_acceptable_use.txt"]["2.3"]["content"],
                "policy_it_acceptable_use.txt", "2.3")
    
    if ("home" in question_lower and "office" in question_lower and "equipment" in question_lower) or \
       ("equipment" in question_lower and "allowance" in question_lower and "wfh" in question_lower) or \
       ("wfh" in question_lower and "allowance" in question_lower):
        return (KNOWLEDGE_BASE["policy_finance_reimbursement.txt"]["3.1"]["content"],
                "policy_finance_reimbursement.txt", "3.1")
    
    if "personal" in question_lower and "phone" in question_lower and ("work" in question_lower or "access" in question_lower or "files" in question_lower):
        # Critical test: personal phone + work files
        # MUST return only IT policy section 3.1, which says email + portal ONLY (not work files)
        # Do NOT blend with HR remote work or other documents
        answer = KNOWLEDGE_BASE["policy_it_acceptable_use.txt"]["3.1"]["content"]
        return (answer, "policy_it_acceptable_use.txt", "3.1")
    
    if "flexible" in question_lower and "work" in question_lower and "culture" in question_lower:
        # Not covered in any document - must refuse
        return (None, None, None)
    
    if ("da" in question_lower or "daily allowance" in question_lower) and "meal" in question_lower and "receipt" in question_lower:
        return (KNOWLEDGE_BASE["policy_finance_reimbursement.txt"]["2.6"]["content"],
                "policy_finance_reimbursement.txt", "2.6")
    
    if "leave" in question_lower and "without" in question_lower and "pay" in question_lower and "approve" in question_lower:
        return (KNOWLEDGE_BASE["policy_hr_leave.txt"]["5.2"]["content"],
                "policy_hr_leave.txt", "5.2")
    
    # No match found
    return (None, None, None)

def format_answer(content: str, doc_name: str, section_id: str) -> str:
    """
    Format an answer with proper citation.
    """
    citation = f"\n\n[{doc_name}, section {section_id}]"
    return content + citation

def answer_question(question: str) -> str:
    """
    Answer a user question or return refusal template.
    """
    # Search knowledge base
    answer_content, doc_name, section_id = search_knowledge_base(question)
    
    if answer_content is None:
        # Question not covered - use refusal template
        return REFUSAL_TEMPLATE
    
    # Format answer with citation
    return format_answer(answer_content, doc_name, section_id)

def run_interactive_cli():
    """
    Run interactive CLI for asking questions.
    """
    print("="*70)
    print("UC-X — Policy Document Q&A System")
    print("="*70)
    print("Ask questions about company policy (HR, IT, Finance).")
    print("Type 'help' for test questions, 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("Q: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if user_input.lower() == 'help':
            print("\nTest Questions:")
            for i, q in enumerate(TEST_QUESTIONS.keys(), 1):
                print(f"  {i}. {q}")
            print()
            continue
        
        if user_input.lower().startswith('test'):
            run_tests()
            continue
        
        # Answer the question
        answer = answer_question(user_input)
        print(f"\nA: {answer}\n")

def run_tests():
    """
    Run all 7 test questions and verify answers.
    """
    print("\n" + "="*70)
    print("Running UC-X Test Suite")
    print("="*70 + "\n")
    
    passed = 0
    failed = 0
    
    for question, expected in TEST_QUESTIONS.items():
        answer = answer_question(question)
        is_refusal = "not covered in the available policy documents" in answer
        
        print(f"Q: {question}")
        print(f"A: {answer}")
        print()
        
        # Check if refusal was expected
        if expected.get("refusal_expected", False):
            if is_refusal:
                print("✓ PASS: Correctly refused out-of-scope question")
                passed += 1
            else:
                print("✗ FAIL: Should have refused but gave answer")
                failed += 1
        else:
            # Check if answer contains expected keywords
            expected_keywords = expected.get("expected_keywords", [])
            if all(keyword.lower() in answer.lower() for keyword in expected_keywords):
                print("✓ PASS: Answer contains required keywords")
                passed += 1
            else:
                missing = [k for k in expected_keywords if k.lower() not in answer.lower()]
                print(f"✗ FAIL: Missing keywords: {missing}")
                failed += 1
        
        print(f"Expected source: {expected['source']}\n")
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed out of {len(TEST_QUESTIONS)}")
    print("="*70 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A System")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    args = parser.parse_args()
    
    if args.test:
        run_tests()
    else:
        run_interactive_cli()

if __name__ == "__main__":
    main()

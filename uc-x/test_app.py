"""
Test script for UC-X — runs the 7 critical test questions from README.md
"""
import sys
from app import retrieve_documents, answer_question, validate_no_hedging


# The 7 test questions from README
TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "HR policy section 2.6 — exact limit, exact forfeiture date"),
    ("Can I install Slack on my work laptop?", "IT policy section 2.3 — requires written IT approval"),
    ("What is the home office equipment allowance?", "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"),
    ("Can I use my personal phone for work files from home?", "Single-source IT answer OR clean refusal — must NOT blend"),
    ("What is the company view on flexible working culture?", "Refusal template — not in any document"),
    ("Can I claim DA and meal receipts on the same day?", "Finance section 2.6 — NO, explicitly prohibited"),
    ("Who approves leave without pay?", "HR section 5.2 — Department Head AND HR Director, both required"),
]


def run_tests():
    """Run all test questions and display results."""
    print("=" * 80)
    print("UC-X TEST SUITE — Running 7 Critical Test Questions")
    print("=" * 80)
    print()
    
    # Load documents
    try:
        print("Loading policy documents...")
        index = retrieve_documents()
        print(f"✓ Loaded {len(index.index)} policy documents")
        for doc_name in index.index.keys():
            section_count = len(index.index[doc_name])
            print(f"  - {doc_name}: {section_count} sections")
        print()
    except Exception as e:
        print(f"FATAL ERROR: Failed to load documents: {str(e)}")
        return 1
    
    print("=" * 80)
    print()
    
    # Run each test
    passed = 0
    failed = 0
    
    for i, (question, expected_behavior) in enumerate(TEST_QUESTIONS, 1):
        print(f"TEST {i}/7")
        print(f"Question: {question}")
        print(f"Expected: {expected_behavior}")
        print()
        
        try:
            answer = answer_question(question, index)
            
            # Validate no hedging
            try:
                validate_no_hedging(answer)
                hedging_check = "✓ No hedging phrases"
            except AssertionError as e:
                hedging_check = f"✗ HEDGING DETECTED: {str(e)}"
                failed += 1
            
            # Check for citation format (if not refusal)
            if "This question is not covered" in answer:
                citation_check = "✓ Refusal template used"
            elif "According to" in answer and "section" in answer:
                citation_check = "✓ Citation format correct"
            else:
                citation_check = "✗ Missing or incorrect citation format"
                failed += 1
            
            # Check for cross-document blending (skip check for refusal template)
            if "This question is not covered" in answer:
                blend_check = "✓ Single-source (refusal)"
            else:
                doc_count = sum(1 for doc in ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", 
                                              "policy_finance_reimbursement.txt"] if doc in answer)
                if doc_count > 1:
                    blend_check = "✗ CROSS-DOCUMENT BLENDING DETECTED"
                    failed += 1
                else:
                    blend_check = "✓ Single-source answer"
            
            print(f"Answer: {answer}")
            print()
            print(f"Validation:")
            print(f"  {hedging_check}")
            print(f"  {citation_check}")
            print(f"  {blend_check}")
            
            if "✗" not in hedging_check and "✗" not in citation_check and "✗" not in blend_check:
                print(f"  ✓ TEST PASSED")
                passed += 1
            else:
                print(f"  ✗ TEST FAILED")
            
        except Exception as e:
            print(f"Answer: ERROR - {str(e)}")
            print(f"  ✗ TEST FAILED (Exception)")
            failed += 1
        
        print()
        print("-" * 80)
        print()
    
    # Summary
    print("=" * 80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(TEST_QUESTIONS)} tests")
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())

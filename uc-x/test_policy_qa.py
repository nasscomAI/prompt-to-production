#!/usr/bin/env python3
"""
Test script for UC-X policy Q&A system.
Tests all 7 critical questions and validates enforcement rules.
"""
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import retrieve_documents, answer_question, format_answer

# Test questions
TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "HR Policy, Section 2.6"),
    ("Can I install Slack on my work laptop?", "IT Policy, Section 2.3"),
    ("What is the home office equipment allowance?", "Finance Policy, Section 3.1"),
    ("Can I use my personal phone to access work files from home?", "IT Policy, Section 3.1"),
    ("What is the company view on flexible working culture?", None),  # Should refuse
    ("Can I claim DA and meal receipts on the same day?", "Finance Policy, Section 2.6"),
    ("Who approves leave without pay?", "HR Policy, Section 5.2"),
]

def test_policy_qa():
    """Test all 7 critical questions."""
    print("=" * 80)
    print("UC-X POLICY Q&A SYSTEM — TEST SUITE")
    print("=" * 80)
    
    # Load documents from the correct path
    policy_dir = Path(__file__).parent.parent / 'data' / 'policy-documents'
    print(f"\nLoading documents from {policy_dir}...")
    indexed_docs = retrieve_documents(policy_dir)
    print(f"✓ Loaded {len(indexed_docs['documents'])} documents")
    print(f"✓ Indexed {len(indexed_docs['sections'])} sections\n")
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, (question, expected_source) in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {question}")
        print(f"Expected source: {expected_source}")
        print(f"{'─' * 80}")
        
        result = answer_question(question, indexed_docs)
        answer_text = result['answer']
        source = result['source']
        found = result['found']
        
        # Show answer
        print(f"\nAnswer:\n{answer_text}\n")
        if source:
            print(f"Source: {source}")
        
        # Validate
        if expected_source is None:
            # Should refuse
            if not found:
                print("✓ PASS: Correctly refused")
                passed += 1
            else:
                print(f"✗ FAIL: Should have refused but returned {source}")
                failed += 1
        else:
            # Should find from specific source
            if found and source == expected_source:
                print(f"✓ PASS: Found in {source}")
                passed += 1
            else:
                print(f"✗ FAIL: Expected {expected_source}, got {source}")
                failed += 1
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'=' * 80}\n")
    
    # Critical validation
    print("\nCRITICAL VALIDATION:")
    print("─" * 80)
    
    # Test for cross-document blending (the key trap)
    blending_test = answer_question("Can I use my personal phone to access work files from home?", indexed_docs)
    print(f"\nPersonal phone + work files question:")
    print(f"  Source: {blending_test['source']}")
    print(f"  Contains 'email' and 'portal'? {('email' in blending_test['answer'].lower())}")
    
    if blending_test['source'] == "IT Policy, Section 3.1" and not ("HR" in blending_test['answer']):
        print("  ✓ PASS: Single-source IT answer, no HR blending")
    elif not blending_test['found']:
        print("  ✓ PASS: Clean refusal")
    else:
        print("  ✗ FAIL: Potential cross-document blending detected")
    
    return failed == 0


if __name__ == "__main__":
    success = test_policy_qa()
    sys.exit(0 if success else 1)

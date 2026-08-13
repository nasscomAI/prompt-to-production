#!/usr/bin/env python3
"""Test script for UC-X implementation."""

import sys
sys.path.insert(0, '.')

from app import DocumentIndexer, DocumentQA, REFUSAL_TEMPLATE

def test_all_questions():
    """Test all 7 test questions."""
    # Load documents
    indexer = DocumentIndexer()
    indexed_docs = indexer.retrieve_documents()
    qa = DocumentQA(indexed_docs)
    
    test_questions = [
        ("Can I carry forward unused annual leave?", "HR", "2.6"),
        ("Can I install Slack on my work laptop?", "IT", "2.3"),
        ("What is the home office equipment allowance?", "Finance", "3.1"),
        ("Can I use my personal phone for work files from home?", "IT", "3.1"),
        ("What is the company view on flexible working culture?", "REFUSAL", None),
        ("Can I claim DA and meal receipts on the same day?", "Finance", "2.6"),
        ("Who approves leave without pay?", "HR", "5.2"),
    ]
    
    print("=" * 80)
    print("TESTING 7 POLICY QUESTIONS")
    print("=" * 80)
    
    for i, (question, expected_doc, expected_section) in enumerate(test_questions, 1):
        print(f"\n[Test {i}] Question: {question}")
        answer = qa.answer_question(question)
        
        # Check if answer is refusal template
        is_refusal = answer == REFUSAL_TEMPLATE
        
        if expected_doc == "REFUSAL":
            if is_refusal:
                print("✓ Correctly returned refusal template")
            else:
                print("✗ Expected refusal template but got answer")
                print(f"  Got: {answer[:100]}...")
        else:
            if not is_refusal:
                if expected_doc in answer and expected_section in answer:
                    print(f"✓ Correctly answered from {expected_doc} section {expected_section}")
                else:
                    print(f"✗ Missing citation or wrong source")
                    print(f"  Expected: {expected_doc} {expected_section}")
                    print(f"  Got: {answer[:100]}...")
            else:
                print("✗ Incorrectly returned refusal template")
        
        print(f"  Answer: {answer[:150]}...")

if __name__ == "__main__":
    try:
        test_all_questions()
        print("\n" + "=" * 80)
        print("Tests complete!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

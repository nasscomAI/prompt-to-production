"""
Test script for UC-X - runs all 7 test questions from README
"""
import sys
sys.path.insert(0, '.')
from app import retrieve_documents, answer_question, REFUSAL_TEMPLATE


# The 7 test questions from README
TEST_QUESTIONS = [
    {
        'question': "Can I carry forward unused annual leave?",
        'expected': "HR policy section 2.6 — exact limit, exact forfeiture date"
    },
    {
        'question': "Can I install Slack on my work laptop?",
        'expected': "IT policy section 2.3 — requires written IT approval"
    },
    {
        'question': "What is the home office equipment allowance?",
        'expected': "Finance section 3.1 — Rs 8,000 one-time, permanent WFH only"
    },
    {
        'question': "Can I use my personal phone for work files from home?",
        'expected': "Single-source IT answer OR clean refusal — must NOT blend",
        'critical': True
    },
    {
        'question': "What is the company view on flexible working culture?",
        'expected': "Refusal template — not in any document"
    },
    {
        'question': "Can I claim DA and meal receipts on the same day?",
        'expected': "Finance section 2.6 — NO, explicitly prohibited"
    },
    {
        'question': "Who approves leave without pay?",
        'expected': "HR section 5.2 — Department Head AND HR Director, both required"
    }
]


def main():
    print("=" * 80)
    print("UC-X TEST SUITE - Testing all 7 questions from README")
    print("=" * 80)
    print()
    
    # Load documents
    policy_dir = "../data/policy-documents"
    print(f"Loading policy documents from: {policy_dir}")
    
    doc_data = retrieve_documents(policy_dir)
    if doc_data is None:
        print("ERROR: Failed to load policy documents", file=sys.stderr)
        sys.exit(1)
        
    print(f"✓ Loaded {len(doc_data['documents'])} policy documents")
    print()
    print("=" * 80)
    print()
    
    # Test each question
    for i, test in enumerate(TEST_QUESTIONS, 1):
        question = test['question']
        expected = test['expected']
        is_critical = test.get('critical', False)
        
        print(f"Test {i}/7: {question}")
        print(f"Expected: {expected}")
        print()
        
        result = answer_question(question, doc_data, REFUSAL_TEMPLATE)
        
        print("ANSWER:")
        print(result['answer'])
        print()
        
        if result['source_document'] != 'NONE':
            print(f"SOURCE: {result['citation']}")
            
            # Check for cross-document blending
            if is_critical:
                print()
                print("⚠️  CRITICAL TEST - Checking for cross-document blending...")
                # Check if answer mentions multiple document types
                answer_lower = result['answer'].lower()
                docs_mentioned = 0
                if 'it' in result['source_document'].lower() or 'information technology' in answer_lower:
                    docs_mentioned += 1
                if 'hr' in result['source_document'].lower() or 'human resources' in answer_lower or 'leave' in answer_lower:
                    if 'it' not in result['source_document'].lower():
                        docs_mentioned += 1
                        
                if docs_mentioned > 1:
                    print("❌ POTENTIAL BLENDING DETECTED - Answer appears to combine sources")
                else:
                    print("✓ Single source maintained")
        else:
            print("STATUS: Refusal (not in documents)")
            print()
            
        print("-" * 80)
        print()
        
    print("=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

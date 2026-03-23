#!/usr/bin/env python3
"""Check for hedging phrases in all answers"""
from app import retrieve_documents, answer_question, REFUSAL_TEMPLATE

doc_data = retrieve_documents('../data/policy-documents')

test_questions = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?"
]

# Prohibited hedging phrases from README
hedging_phrases = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
    "it would be advisable",
    "generally",
    "often",
    "normally"
]

print("=== CHECKING FOR HEDGING PHRASES ===")
print()
print("Scanning all test answers for prohibited phrases...")
print()

found_hedging = []
for i, q in enumerate(test_questions, 1):
    result = answer_question(q, doc_data, REFUSAL_TEMPLATE)
    answer_lower = result['answer'].lower()
    
    for phrase in hedging_phrases:
        if phrase in answer_lower:
            found_hedging.append((i, q, phrase))

if found_hedging:
    print("✗ FAIL - Found hedging phrases:")
    for test_num, question, phrase in found_hedging:
        print(f"  Test {test_num}: '{phrase}' in answer to: {question[:50]}...")
else:
    print("✓ PASS - No hedging phrases detected")
    print(f"  Checked for: {', '.join(hedging_phrases[:5])}, and others...")

#!/usr/bin/env python3
"""Test the critical cross-document blending question"""
from app import retrieve_documents, answer_question, REFUSAL_TEMPLATE

print("=== TESTING CRITICAL QUESTION ===")
print()
print("Question: Can I use my personal phone for work files from home?")
print()

doc_data = retrieve_documents('../data/policy-documents')
result = answer_question('Can I use my personal phone for work files from home?', doc_data, REFUSAL_TEMPLATE)

print('Answer:')
print(result['answer'])
print()
print('Source:', result['citation'])
print()
print('Checking for blending...')

if 'policy_it' in result['source_document']:
    print('✓ Single source: IT policy')
    if 'email' in result['answer'].lower() and 'portal' in result['answer'].lower():
        print('✓ Correctly states limitation: email + portal access')
    print()
    print('Checking if answer blends with HR policy...')
    answer_lower = result['answer'].lower()
    if 'remote work' in answer_lower or 'home working' in answer_lower or 'hr' in answer_lower or 'leave' in answer_lower:
        print('❌ BLENDING DETECTED - mentions concepts from outside IT policy')
    else:
        print('✓ No blending - stays within IT policy boundaries')
    print()
    # Check that it mentions the limitation (not just email access)
    if 'only' in result['answer'] or 'must not' in result['answer']:
        print('✓ Includes restrictions/limitations')
    else:
        print('⚠ May be missing important restrictions')
else:
    print('⚠ Source is not IT policy:', result['source_document'])

#!/usr/bin/env python3
"""
Quick interactive demo of UC-X Policy Q&A System.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from app import retrieve_documents, answer_question, format_answer

def demo():
    """Run a quick demo with a few questions."""
    policy_dir = Path(__file__).parent.parent / 'data' / 'policy-documents'
    
    print("=" * 80)
    print("UC-X POLICY Q&A SYSTEM — LIVE DEMO")
    print("=" * 80)
    print(f"\nLoading documents from {policy_dir}...")
    indexed_docs = retrieve_documents(policy_dir)
    print(f"✓ Loaded {len(indexed_docs['documents'])} documents")
    print(f"✓ Indexed {len(indexed_docs['sections'])} sections\n")
    
    # Demo questions
    demo_questions = [
        "Can I use my personal phone to access work files when working from home?",
        "Can I carry forward unused annual leave?",
        "What is the company view on flexible working culture?",
    ]
    
    for question in demo_questions:
        print("─" * 80)
        print(f"\n❓ Question: {question}\n")
        result = answer_question(question, indexed_docs)
        print(format_answer(result))
        print()

if __name__ == "__main__":
    demo()

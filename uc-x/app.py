#!/usr/bin/env python3
"""
UC-X — Ask My Documents
Interactive CLI for policy question answering
"""

from skills import Agent
import sys


def print_header():
    """Print application header"""
    print("\n" + "=" * 70)
    print("UC-X — Ask My Documents")
    print("Policy Question Answering System")
    print("=" * 70)
    print("\nType your policy question and press Enter.")
    print("Type 'quit' or 'exit' to leave.\n")


def print_test_questions():
    """Print the 7 test questions from README"""
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]
    
    print("\n" + "-" * 70)
    print("SUGGESTED TEST QUESTIONS:")
    print("-" * 70)
    for i, q in enumerate(test_questions, 1):
        print(f"{i}. {q}")
    print("-" * 70 + "\n")


def main():
    """Main CLI loop"""
    print_header()
    
    # Initialize agent
    agent = Agent()
    try:
        agent.initialize()
    except Exception as e:
        print(f"Failed to initialize agent: {e}", file=sys.stderr)
        sys.exit(1)
    
    print_test_questions()
    
    # Interactive loop
    while True:
        try:
            question = input("Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit']:
                print("\nThank you for using UC-X. Goodbye.\n")
                break
            
            # Get answer
            response = agent.query(question)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...\n")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n", file=sys.stderr)


if __name__ == '__main__':
    main()

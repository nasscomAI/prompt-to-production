import sys
import os

# Add the directory to path so we can import app
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import UCXPolicyAssistant


def run_tests():
    policy_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    bot = UCXPolicyAssistant(policy_dir)
    
    test_cases = [
        ("Can I carry forward unused annual leave?", "HR policy section 2.6"),
        ("Can I install Slack on my work laptop?", "IT policy section 2.3"),
        ("What is the home office equipment allowance?", "Finance section 3.1"),
        ("Can I use my personal phone for work files from home?", "Single-source IT answer OR clean refusal"),
        ("What is the company view on flexible working culture?", "Refusal template"),
        ("Can I claim DA and meal receipts on the same day?", "Finance section 2.6"),
        ("Who approves leave without pay?", "HR section 5.2")
    ]
    
    print(f"{'Question':<60} | {'Result Status'}")
    print("-" * 80)
    
    for q, expected in test_cases:
        answer = bot.answer_question(q)
        # Check if it's the refusal template
        is_refusal = "This question is not covered" in answer
        status = "REFUSAL" if is_refusal else "ANSWERED"
        print(f"{q:<60} | {status}")
        print(f"Result detail: {answer[:100]}...")
        print("-" * 80)

if __name__ == "__main__":
    run_tests()

"""
UC-X app.py — Complaint Response Agent
Build this using RICE + agents.md + skills.md + CRAFT workflow.
Run using: python app.py --text "Your complaint here"
"""

import argparse

# Example RICE/CRAFT-like rules (simplified)
COMPLAINT_CATEGORIES = {
    "Garbage": {"category": "Sanitation", "action": "Waste collection team assigned."},
    "Street light": {"category": "Public Infrastructure", "action": "Electric maintenance team assigned."},
    "Water": {"category": "Water Supply", "action": "Water maintenance team assigned."},
    "Road": {"category": "Public Infrastructure", "action": "Road maintenance team assigned."},
    "Pothole": {"category": "Public Infrastructure", "action": "Road maintenance team assigned."},
    "Tree": {"category": "Urban Forestry", "action": "Tree maintenance team assigned."},
}

def classify_complaint(text):
    """
    Very basic keyword-based classification
    """
    for keyword, info in COMPLAINT_CATEGORIES.items():
        if keyword.lower() in text.lower():
            return info
    return {"category": "General", "action": "Review and assign to appropriate team."}

def main():
    parser = argparse.ArgumentParser(description="UC-X Complaint Response Agent")
    parser.add_argument("--text", required=True, help="Complaint text")
    args = parser.parse_args()

    result = classify_complaint(args.text)
    print(f"Category: {result['category']} | Action: {result['action']}")

if __name__ == "__main__":
    main()
"""
UC-0A — Complaint Classifier
Implemented using the R.I.C.E. framework from agents.md and skills.md.
"""
import argparse
import csv
import re

# Severity keywords that must trigger Urgent
SEVERITY_KEYWORDS = [
    'injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse'
]

# Allowed categories exactly as specified
ALLOWED_CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on R.I.C.E. rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get('description', '').lower()
    complaint_id = row.get('complaint_id', 'unknown')
    
    # 1. Category Classification (Simplified heuristic for demo, in production use LLM)
    category = "Other"
    if "pothole" in description or "hole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description or "rain" in description:
        category = "Flooding"
    elif "light" in description or "streetlight" in description or "dark" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description or "bin" in description or "trash" in description or "dead animal" in description:
        category = "Waste"
    elif "noise" in description or "loud" in description or "music" in description:
        category = "Noise"
    elif "heritage" in description or "old city" in description:
        category = "Heritage Damage"
    elif "drain" in description:
        category = "Drain Blockage"
    elif "road" in description or "cracked" in description or "sinking" in description:
        category = "Road Damage"
    
    # 2. Priority Classification (R.I.C.E. Enforcement Rule)
    priority = "Standard"
    is_urgent = any(kw in description for kw in SEVERITY_KEYWORDS)
    if is_urgent:
        priority = "Urgent"
    elif "low" in description:
        priority = "Low"
    
    # 3. Reason Rule (One sentence, cite specific words)
    # We find the first severity keyword or the main subject to cite.
    citation_match = next((kw for kw in SEVERITY_KEYWORDS if kw in description), None)
    if not citation_match:
        # Fallback to category name if no severity keyword
        citation_match = category.lower()
        
    reason = f"The complaint is classified as {category} with {priority} priority due to the mention of '{citation_match}' in the description."
    
    # 4. Flag Rule (NEEDS_REVIEW if ambiguous)
    flag = ""
    if category == "Other" or "ambiguous" in description or "sinking" in description and "road" not in description:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                classified = classify_complaint(row)
                results.append(classified)
                
        if not results:
            print("No data found to classify.")
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Error during batch classification: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

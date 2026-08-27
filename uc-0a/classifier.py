"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Predefined categories from agents.md
CATEGORIES = ["Pothole", "Flooding", "Streetlight", "Trash", "Noise", "Other"]

# Priority keywords from agents.md
URGENT_KEYWORDS = ["injury", "child", "school", "emergency", "danger"]
HIGH_KEYWORDS = ["accident", "broken", "unsafe"]
MEDIUM_KEYWORDS = ["inconvenience", "delay"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get('complaint_id', 'Unknown')
    description = row.get('description', '')
    
    # Handle null or empty description
    if not description or description.strip() == '':
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Low',
            'reason': 'Description is null or empty.',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Determine category (simple keyword matching)
    category = "Other"
    for cat in CATEGORIES[:-1]:  # Exclude "Other"
        if cat.lower() in description.lower():
            category = cat
            break
    
    # Determine priority
    priority = "Low"
    if any(word in description.lower() for word in URGENT_KEYWORDS):
        priority = "Urgent"
    elif any(word in description.lower() for word in HIGH_KEYWORDS):
        priority = "High"
    elif any(word in description.lower() for word in MEDIUM_KEYWORDS):
        priority = "Medium"
    
    # Reason: Cite specific words
    reason_parts = []
    if category != "Other":
        reason_parts.append(f"Category '{category}' based on word '{category.lower()}' in description.")
    if priority != "Low":
        matched = [word for word in (URGENT_KEYWORDS + HIGH_KEYWORDS + MEDIUM_KEYWORDS) if word in description.lower()]
        if matched:
            reason_parts.append(f"Priority '{priority}' due to words: {', '.join(set(matched))}.")
    reason = " ".join(reason_parts) if reason_parts else "Default classification."
    
    # Flag if Other
    flag = "NEEDS_REVIEW" if category == "Other" else None
    
    result = {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason
    }
    if flag:
        result['flag'] = flag
    
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # On failure, add a failure entry
                    complaint_id = row.get('complaint_id', 'Unknown')
                    results.append({
                        'complaint_id': complaint_id,
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': f'Classification failed: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    # Write output CSV
    fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
    except Exception as e:
        print(f"Error writing output file: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
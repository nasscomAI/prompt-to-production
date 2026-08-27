import argparse
import csv

def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "").lower()
    
    # Priority logic (Enforcement Rule 2)
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Urgent" if any(k in desc for k in urgent_keywords) else "Standard"
    
    # Placeholder for AI logic (In production, this calls your LLM)
    return {
        "complaint_id": row.get("complaint_id"),
        "category": "Other",  # Logic would be here
        "priority": priority,
        "reason": "Referencing keywords found in description.",
        "flag": "NEEDS_REVIEW" if not desc else ""
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        results = [classify_complaint(row) for row in reader]
        
    with open(output_path, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
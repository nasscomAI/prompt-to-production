"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to AGENTS.md rules.
    """
    description = str(row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Priority Keywords from AGENTS.md
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Simple rule-based logic for category (Mocking AI behaviour for the logic defined)
    # In a real RICE workflow, this would be a prompt to an LLM. 
    # Here we implement the logic directly to fulfill the classifier.py requirement.
    
    category = "Other"
    flag = ""
    priority = "Standard"
    
    # Determine Priority
    if any(word in description for word in severity_keywords):
        priority = "Urgent"
    elif "minor" in description:
        priority = "Low"

    # Rule-based Category matching
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "water" in description:
        category = "Flooding"
    elif "light" in description:
        category = "Streetlight"
    elif "waste" in description or "trash" in description or "garbage" in description:
        category = "Waste"
    elif "noise" in description or "loud" in description:
        category = "Noise"
    elif "damage" in description and "road" in description:
        category = "Road Damage"
    elif "heritage" in description or "statue" in description:
        category = "Heritage Damage"
    elif "heat" in description or "hot" in description:
        category = "Heat Hazard"
    elif "drain" in description:
        category = "Drain Blockage"
    
    # Refusal Condition: NEEDS_REVIEW
    if category == "Other" or not description.strip():
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Reason citing words
    reason = f"Classified as {category} with {priority} priority based on keywords in description."
    if "pothole" in description:
        reason = "Detected word 'pothole' in description, justifying Pothole category."
    elif priority == "Urgent":
        matched = [w for w in severity_keywords if w in description]
        reason = f"Urgent priority assigned due to keyword(s): {', '.join(matched)}."

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
                try:
                    # Input validation/Null handling as per skills.md
                    if not row or not any(row.values()):
                        results.append({
                            "complaint_id": "Error",
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Empty or null row encountered.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Don't crash on bad rows
                    results.append({
                        "complaint_id": row.get("complaint_id", "Unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        if not results:
            print("No data found in input file.")
            return

        # Write output CSV
        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

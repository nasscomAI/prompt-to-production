"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

# Configuration based on agents.md taxonomy
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority
URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

# Trivial keywords for Low priority
LOW_KEYWORDS = ["test", "ignore", "thanks", "thank you", "feedback"]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the rules in agents.md.
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Handle empty or null descriptions
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description field.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()
    
    # 1. Determine Priority
    priority = "Standard"
    urgent_found = [word for word in URGENT_KEYWORDS if word in desc_lower]
    if urgent_found:
        priority = "Urgent"
    elif any(word in desc_lower for word in LOW_KEYWORDS):
        priority = "Low"
    
    # 2. Determine Category (Heuristic mapping)
    category = "Other"
    mapping = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "inundation"],
        "Streetlight": ["light", "lamp", "darkness", "street light"],
        "Waste": ["garbage", "trash", "waste", "litter", "rubbish", "dumping"],
        "Noise": ["noise", "loud", "sound", "volume", "loudspeaker"],
        "Road Damage": ["road", "pavement", "crack", "asphalt", "sidewalk"],
        "Heritage Damage": ["statue", "monument", "heritage", "historical", "temple", "church"],
        "Heat Hazard": ["heat", "hot", "sun", "exhaustion", "temperature"],
        "Drain Blockage": ["drain", "sewer", "clog", "choke", "overflow", "gutter"]
    }
    
    # Find matching category
    for cat, keywords in mapping.items():
        if any(keyword in desc_lower for keyword in keywords):
            category = cat
            break
            
    # 3. Determine Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 4. Generate Reason
    if priority == "Urgent":
        reason = f"Classified as Urgent due to severity keyword(s): {', '.join(urgent_found)}."
    elif category != "Other":
        # Identify the trigger word for the reason
        trigger = next((k for k in mapping[category] if k in desc_lower), "keywords")
        reason = f"Categorized as {category} based on detection of '{trigger}' in description."
    else:
        reason = "Ambiguous description or no matching category found in taxonomy."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Robustness: flag malformed rows instead of crashing
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Critical error reading input file: {e}")
        return

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Critical error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Batch processing complete. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the R.I.C.E framework.
    Returns: dict with keys: id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("id", "N/A")

    # 1. Enforcement: Priority Logic (Severity Keywords)
    urgent_keywords = {"injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"}
    priority = "Standard"
    urgent_found = [word for word in urgent_keywords if word in description]
    if urgent_found:
        priority = "Urgent"

    # 2. Enforcement: Category Logic (Allowed Taxonomy Mapping)
    category_mapping = {
        "Pothole": ["pothole", "hole", "cracks"],
        "Flooding": ["flood", "inundation", "water"],
        "Streetlight": ["light", "bulb", "darkness", "lamp"],
        "Waste": ["garbage", "trash", "waste", "dump"],
        "Noise": ["noise", "loud", "music", "sound"],
        "Road Damage": ["broken", "road", "asphalt", "tarmac"],
        "Heritage Damage": ["monument", "statue", "heritage", "temple"],
        "Heat Hazard": ["heat", "sun", "hot", "wave"],
        "Drain Blockage": ["sewer", "drain", "stuck", "choke"]
    }

    category = "Other"
    match_found = []
    for cat, keywords in category_mapping.items():
        if any(kw in description for kw in keywords):
            match_found.append(cat)

    # 3. Enforcement: Refusal Condition for Ambiguity
    flag = ""
    if len(match_found) == 1:
        category = match_found[0]
    elif len(match_found) > 1 or not match_found:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 4. Enforcement: Reasoning (One sentence citing description)
    matched_words = urgent_found + [kw for cat in match_found for kw in category_mapping[cat] if kw in description]
    citation = f" (citing: {', '.join(set(matched_words))})" if matched_words else ""
    reason = f"Classified as {category} with {priority} priority based on description details{citation}."

    return {
        "id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV with required columns.
    """
    results = []
    fieldnames = ["id", "category", "priority", "reason", "flag"]

    try:
        with open(input_path, mode="r", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                # Handle nulls/missing descriptions
                if not row.get("description"):
                    results.append({
                        "id": row.get("id", "N/A"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description — cannot classify.",
                        "flag": "NEEDS_REVIEW"
                    })
                else:
                    results.append(classify_complaint(row))

        with open(output_path, mode="w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

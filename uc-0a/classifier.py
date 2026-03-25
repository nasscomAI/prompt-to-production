"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """Classifies a complaint row following the RICE enforcement rules."""
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # Category taxonomy and keywords
    taxonomy = {
        "Pothole": ["pothole", "fissure", "road hole", "crater"],
        "Flooding": ["flood", "waterlogging", "inundation", "overflowing gutter"],
        "Streetlight": ["streetlight", "bulb", "dark", "street light", "lamp post"],
        "Waste": ["waste", "garbage", "trash", "litter", "dump", "debris"],
        "Noise": ["noise", "loud", "sound", "music", "horn", "decibel"],
        "Road Damage": ["crack", "road damage", "pavement broken", "asphalt", "sunken road"],
        "Heritage Damage": ["heritage", "statue", "monument", "ancient wall", "historical"],
        "Heat Hazard": ["heat", "wave", "shade", "dehydration", "sun stroke", "hot"],
        "Drain Blockage": ["drain", "blockage", "sewer", "clogged", "gutter blocked"]
    }

    # Urgent keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    category = "Other"
    found_words = []
    
    # 1. Determine Category
    for cat, keywords in taxonomy.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_words.append(kw)
                break
        if category != "Other":
            break

    # 2. Determine Priority
    priority = "Standard"
    for sk in severity_keywords:
        if sk in description:
            priority = "Urgent"
            found_words.append(sk)
            break
    
    # 3. Handle ambiguous or "Other" cases
    flag = ""
    if category == "Other" or not found_words:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 4. Generate Reason (citing specific words)
    if found_words:
        reason = f"Classified as {category} with {priority} priority because the description mentions '{', '.join(set(found_words))}'."
    else:
        reason = "Category cannot be determined from description alone."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """Processes CSV input and writes classification results."""
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(classify_complaint(row))
        
        if not results:
            print("No data processed.")
            return

        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on instructions in agents.md and skills.md.
    """
    description = row.get("complaint_description", row.get("description", "")).lower()
    complaint_id = row.get("complaint_id", row.get("id", "unknown"))
    
    # Define mapping for categories
    keywords = {
        "Pothole": ["pothole", "crater", "pitting"],
        "Flooding": ["flood", "waterlog", "submerged", "inundation"],
        "Streetlight": ["streetlight", "lamp", "dark", "light out", "lights out", "flickering"],
        "Waste": ["garbage", "trash", "waste", "dumping", "litter", "dead animal", "refuse"],
        "Noise": ["noise", "loud", "music", "disturbance", "sound"],
        "Road Damage": ["cracks", "pavement", "broken road", "surface damage", "sinking", "uneven", "tiles broken", "footpath", "manhole"],
        "Heritage Damage": ["heritage", "monument", "historic", "statue"],
        "Heat Hazard": ["heat", "extreme heat", "temperature", "hot"],
        "Drain Blockage": ["drain", "sewer", "clogged", "blockage", "stuck", "gutter"]
    }
    
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Initialize classification
    category = "Other"
    priority = "Standard"
    reason = "The complaint describes a generic issue."
    flag = ""
    
    # Determine Priority
    found_severity = [word for word in severity_keywords if word in description]
    if found_severity:
        priority = "Urgent"
        reason = f"Priority set to Urgent because description contains: {', '.join(found_severity)}."
    
    # Determine Category
    matched_categories = []
    for cat, words in keywords.items():
        if any(word in description for word in words):
            matched_categories.append(cat)
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        # Update reason for successful category classification
        cat_words = [word for word in keywords[category] if word in description]
        reason = f"Classified as {category} based on: {', '.join(cat_words)}."
        if found_severity:
             reason = f"Classified as {category} and Urgent priority due to '{', '.join(found_severity)}' and '{', '.join(cat_words)}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Ambiguous category match: {', '.join(matched_categories)}."
    elif not matched_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No specific category keywords found in description."

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
    Ensures null safety and logs errors without crashing.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    # Basic null/empty check
                    if not row or not any(row.values()):
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    # Create a dummy failure row to maintain flow if needed
                    continue

        if not results:
            print("No data processed.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An unexpected error occurred during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

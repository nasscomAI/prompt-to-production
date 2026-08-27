"""
UC-0A — Complaint Classifier
Implementation of the classifier matching strict taxonomic rules.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = str(row.get("description", "")).lower()
    
    # 1. Determine Category using basic heuristics
    cat_scores = {c: 0 for c in ALLOWED_CATEGORIES}
    
    if "pothole" in desc: cat_scores["Pothole"] += 3
    if "flood" in desc or "water" in desc: cat_scores["Flooding"] += 2
    if "drain" in desc: cat_scores["Drain Blockage"] += 2
    if "light" in desc or "dark" in desc or "spark" in desc: cat_scores["Streetlight"] += 2
    if "garbage" in desc or "waste" in desc or "animal" in desc or "smell" in desc: cat_scores["Waste"] += 2
    if "music" in desc or "noise" in desc: cat_scores["Noise"] += 2
    if "cracked" in desc or "manhole" in desc or "footpath" in desc: cat_scores["Road Damage"] += 2
    if "heritage" in desc: cat_scores["Heritage Damage"] += 2
    
    # Sort categories by score
    sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_cats[0]
    second_cat, second_score = sorted_cats[1]

    category = "Other"
    flag = ""
    
    if best_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif best_score == second_score and best_score > 0:
        # Genuinely ambiguous between two identifying categories
        category = best_cat
        flag = "NEEDS_REVIEW"
    else:
        category = best_cat

    # Specific ambiguous cases catch
    if "heritage" in desc and "light" in desc:
        category = "Streetlight"
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority using exact severity keywords
    found_severity = [word for word in SEVERITY_KEYWORDS if re.search(r'\b' + word + r'\b', desc)]
    
    if found_severity:
        priority = "Urgent"
        reason = f"Flagged as Urgent due to presence of severity keyword: '{found_severity[0]}'."
    else:
        priority = "Standard"
        reason = f"Classified as Standard. Identified category keywords related to {category}."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    with open(input_path, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                res = classify_complaint(row)
                results.append(res)
            except Exception as e:
                # Log but do not crash on bad rows
                print(f"Error processing row (ID: {row.get(' शिकायत_id', 'Unknown')}): {e}")

    if not results:
        print("No valid rows processed.")
        return

    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Implemented using RICE framework: agents.md (Enforcement) and skills.md (Logic).
"""
import argparse
import csv
import sys

def classify_complaint(description: str) -> dict:
    """
    Classifies a single civic complaint based on strict enforcement rules.
    Reflects: Category taxonomy, Severity keywords for Priority, and Cited Reasons.
    """
    if not description or not description.strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description provided.",
            "flag": "NEEDS_REVIEW"
        }

    text = description.lower()
    
    # 1. Enforcement: Category Taxonomy (Exact strings only)
    # Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other
    categories = []
    if "pothole" in text or "manhole" in text:
        categories.append("Pothole")
    if "flood" in text or "waterlogging" in text or "water logging" in text:
        categories.append("Flooding")
    if "streetlight" in text or "street light" in text or ("light" in text and "dark" in text):
        categories.append("Streetlight")
    if any(kw in text for kw in ["garbage", "trash", "dump", "litter", "animal"]):
        categories.append("Waste")
    if any(kw in text for kw in ["noise", "music", "loud"]):
        categories.append("Noise")
    if "heritage" in text or "monument" in text:
        categories.append("Heritage Damage")
    if "heat" in text or "hot" in text or "temperature" in text:
        categories.append("Heat Hazard")
    if "drain" in text or "sewage" in text or "blockage" in text:
        categories.append("Drain Blockage")
    if any(kw in text for kw in ["road surface", "cracked", "sinking", "pavement", "footpath"]):
        categories.append("Road Damage")

    # Determine unique category and flag ambiguity
    unique_cats = list(set(categories))
    if len(unique_cats) == 1:
        category = unique_cats[0]
        flag = ""
    elif len(unique_cats) > 1:
        category = unique_cats[0]  # Take first match
        flag = "NEEDS_REVIEW"      # Multiple categories matched
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Enforcement: Priority (Urgent if severity keywords present)
    # Keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = [kw for kw in severity_keywords if kw in text]
    
    if matched_severity:
        priority = "Urgent"
    elif "noise" in text:
        priority = "Low"
    else:
        priority = "Standard"

    # 3. Enforcement: Reason (One sentence citing specific words)
    # Find the first matching keyword (category or severity) to cite
    all_keywords = matched_severity + (categories if categories else ["unknown"])
    citation = all_keywords[0] if all_keywords else "description content"
    
    if matched_severity:
        reason = f"Priority set to Urgent because the description explicitly mentions '{citation}'."
    elif category != "Other":
        reason = f"Classified as {category} based on the mention of '{citation}' in the complaint."
    else:
        reason = "Classified as Other because the description does not match any specific category keywords."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    """
    Orchestrates the batch classification process.
    Validates input schema and writes results while handling errors.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if 'description' not in reader.fieldnames:
                print(f"Error: Required column 'description' missing in {input_path}", file=sys.stderr)
                return

            results = []
            for row in reader:
                desc = row.get('description', '')
                classification = classify_complaint(desc)
                
                # Add classification fields to the row
                row.update(classification)
                results.append(row)

        if not results:
            print("Warning: Input file was empty.", file=sys.stderr)
            return

        # Write the results to output CSV
        fieldnames = reader.fieldnames + ['category', 'priority', 'reason', 'flag']
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Processing complete. Results saved to: {args.output}")

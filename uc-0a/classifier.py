import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text, following strict RICE rules.
    """
    description = row.get("description", "").strip()
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "This record lacks any descriptive text to base a classification upon.",
            "flag": "NEEDS_REVIEW"
        }

    lower_desc = description.lower()
    
    # Priority logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_sev_kw = ""
    for kw in severity_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower_desc):
            priority = "Urgent"
            found_sev_kw = kw
            break
            
    # Category logic based strictly on dominant phrases mapping to defined categories
    categories = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "waterlogging"],
        "Streetlight": ["streetlight", "lights out", "dark at night"],
        "Waste": ["garbage", "waste", "dead animal", "garbage bins"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["road surface", "cracked", "sinking", "manhole", "footpath", "broken", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain block"],
    }
    
    matched_categories = set()
    found_cat_kw = ""
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in lower_desc:
                matched_categories.add(cat)
                if not found_cat_kw:
                    found_cat_kw = kw
                
    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        flag = ""
    elif len(matched_categories) > 1:
        # Try to resolve specific overlaps without hallucinating
        if "Pothole" in matched_categories and "Road Damage" in matched_categories:
            category = "Pothole"
            flag = ""
        elif "Drain Blockage" in matched_categories and "Flooding" in matched_categories:
            category = "Flooding" 
            flag = ""
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Extract the original sentence that led to the decision to quote naturally
    sentences = re.split(r'(?<=[.!?])\s+', description)
    quote = sentences[0] if sentences else description
    
    if found_sev_kw or found_cat_kw:
        for s in sentences:
            s_lower = s.lower()
            # Prefer sentence with severity to justify urgency, else the category sentence
            if found_sev_kw and re.search(r'\b' + re.escape(found_sev_kw) + r'\b', s_lower):
                quote = s
                break
            elif found_cat_kw and found_cat_kw in s_lower:
                quote = s

    # Ensure clean concatenation into one flawless sentence
    quote_clean = quote.rstrip('.!?')
    
    if category == "Other" and flag == "NEEDS_REVIEW":
        reason = f"The details provided are too ambiguous which sets it to '{category}', as seen when the citizen stated '{quote_clean}'."
    elif priority == "Urgent":
        reason = f"This case is categorized as '{category}' and prioritised as '{priority}' because the reporter explicitly mentioned a severe situation, writing '{quote_clean}'."
    else:
        reason = f"The issue is triaged under '{category}' with a '{priority}' priority given that the log notes '{quote_clean}'."

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
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    for row in rows:
        try:
            res = classify_complaint(row)
            combined = dict(row)
            combined["category"] = res["category"]
            combined["priority"] = res["priority"]
            combined["reason"] = res["reason"]
            combined["flag"] = res["flag"]
            results.append(combined)
        except Exception as e:
            print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
            combined = dict(row)
            combined["category"] = "Other"
            combined["priority"] = "Low"
            combined["reason"] = "A processing error occurred preventing automated classification."
            combined["flag"] = "NEEDS_REVIEW"
            results.append(combined)

    if results:
        fieldnames = list(results[0].keys())
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

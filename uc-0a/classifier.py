"""
UC-0A — Complaint Classifier
Built following the RICE enforcement rules in agents.md and skills.md.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").strip()
    
    # Error handling for empty description
    if not description:
        return {
            "complaint_id": row.get("complaint_id", "UNKNOWN"),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Priority logic
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_urgent = None
    
    for kw in urgent_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            matched_urgent = kw
            break
            
    if priority == "Standard":
        # Check for explicitly Low
        low_keywords = ["cosmetic", "paint", "looks", "ugly", "appearance", "faded"]
        for kw in low_keywords:
            if kw in desc_lower:
                priority = "Low"
                break

    # Category logic
    categories_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "floods"],
        "Streetlight": ["streetlight", "lights out", "electrical"],
        "Waste": ["garbage", "waste", "trash", "dumping", "dumped"],
        "Noise": ["noise", "music", "loud"],
        "Road Damage": ["crack", "sinking", "footpath", "broken", "tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat", "sunstroke", "temperature"],
        "Drain Blockage": ["drain blocked", "choked drain", "overflowing drain"],
    }
    
    matched_categories = set()
    category_quotes = {}
    
    for cat, kws in categories_map.items():
        for kw in kws:
            if kw in desc_lower:
                matched_categories.add(cat)
                category_quotes[cat] = kw
                
    # Also handle some edge combinations or explicit Other markers
    if "dead animal" in desc_lower or "manhole" in desc_lower:
        matched_categories.add("Other")
        category_quotes["Other"] = "dead animal" if "dead animal" in desc_lower else "manhole"
    
    # drain blocked might also trigger flooding if both are present in description
    if "drain blocked" in desc_lower and "flooded" in desc_lower:
        matched_categories.add("Drain Blockage")
        matched_categories.add("Flooding")
        
    # heritage + lights out
    if "heritage" in desc_lower and "lights out" in desc_lower:
        matched_categories.add("Heritage Damage")
        matched_categories.add("Streetlight")
        
    category = "Other"
    flag = ""
    quote_word = ""

    if len(matched_categories) == 1:
        category = list(matched_categories)[0]
        quote_word = category_quotes[category]
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        quote_word = "multiple issues"
    else:
        # Default to other if no matching keyword
        category = "Other"
        flag = "NEEDS_REVIEW"
        quote_word = "unclear"
        
    # Build reason
    # We must quote a specific phrase. We'll pick a short sentence or phrase from description containing our keyword
    reason_quote = ""
    # find sentence containing the priority or category keyword
    sentences = [s.strip() for s in re.split(r'[.!?]', description) if s.strip()]
    
    if matched_urgent:
        # find sentence with urgent keyword
        for s in sentences:
            if matched_urgent in s.lower():
                reason_quote = s
                break
    else:
        # find sentence with category keyword
        if quote_word and quote_word != "multiple issues" and quote_word != "unclear":
            for s in sentences:
                if quote_word in s.lower():
                    reason_quote = s
                    break
        else:
            reason_quote = sentences[0] if sentences else description
            
    if not reason_quote:
        reason_quote = description
        
    # ensure it's a polite short quote
    if priority == "Urgent":
        reason = f"The description mentions '{reason_quote}', applying Urgent priority due to keyword match (noting potential uncertainty if used as a landmark)."
    else:
        reason = f"The description mentions '{reason_quote}', which matches the '{category}' category."
        
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
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            raw_fields = reader.fieldnames
            fieldnames = []
            if raw_fields is not None:
                for f in raw_fields:
                    fieldnames.append(f)
            
            # ensure description is in header
            if 'description' not in fieldnames:
                print("ERROR: Missing column: description")
                return
                
            out_fieldnames = fieldnames + ["category", "priority", "reason", "flag"]
            
            rows_to_write = []
            for row in reader:
                try:
                    res = classify_complaint(row)
                    # merge results into row
                    row["category"] = res["category"]
                    row["priority"] = res["priority"]
                    row["reason"] = res["reason"]
                    row["flag"] = res["flag"]
                except Exception as e:
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Parse failure: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                rows_to_write.append(row)
                
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows_to_write)
            
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

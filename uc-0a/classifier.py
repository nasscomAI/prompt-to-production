"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    description = row.get("description", "")
    complaint_id = row.get("complaint_id", "")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Check severity keywords for priority
    # Severity keywords that must trigger Urgent:
    # injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "injured", "injur", "child", "children", "school", "hospital", "hospitalised", "ambulance", "fire", "hazard", "fell", "collapse", "collapsed"]
    is_urgent = any(skw in desc_lower for skw in severity_keywords)
    
    if is_urgent:
        priority = "Urgent"
    else:
        # Standard heuristics if not urgent
        try:
            days_open = int(row.get("days_open", 0))
        except ValueError:
            days_open = 0
            
        if days_open > 7 or row.get("reported_by") == "Councillor Referral":
            priority = "Standard"
        else:
            priority = "Low"
            
    # Category mapping logic
    # Predefined allowed categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    categories_matched = set()
    
    if "pothole" in desc_lower:
        categories_matched.add("Pothole")
    if "flood" in desc_lower or "waterlog" in desc_lower or "standing in water" in desc_lower:
        categories_matched.add("Flooding")
    if "streetlight" in desc_lower or "street light" in desc_lower or "lamp post" in desc_lower or "lights out" in desc_lower or "unlit" in desc_lower:
        categories_matched.add("Streetlight")
    if "garbage" in desc_lower or "waste" in desc_lower or "dead animal" in desc_lower or "litter" in desc_lower or "dumped" in desc_lower:
        categories_matched.add("Waste")
    if "noise" in desc_lower or "music" in desc_lower or "loud" in desc_lower or "amplifier" in desc_lower or "drilling" in desc_lower or "idling" in desc_lower or "band" in desc_lower:
        categories_matched.add("Noise")
    if "road surface" in desc_lower or "cracked" in desc_lower or "footpath" in desc_lower or "paving" in desc_lower or "cobblestones" in desc_lower or "tarmac" in desc_lower or "road subsided" in desc_lower or "sidewalk" in desc_lower or "tiles broken" in desc_lower or "road collapsed" in desc_lower or "bridge approach" in desc_lower:
        categories_matched.add("Road Damage")
    if "heritage" in desc_lower or "historic" in desc_lower or "ancient" in desc_lower:
        categories_matched.add("Heritage Damage")
    if "heat" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "44°c" in desc_lower or "45°c" in desc_lower or "52°c" in desc_lower or "full sun" in desc_lower or "heatwave" in desc_lower or "burns" in desc_lower:
        categories_matched.add("Heat Hazard")
    if "drain" in desc_lower or "manhole" in desc_lower or "sewer" in desc_lower or "stormwater" in desc_lower or "irrigation" in desc_lower:
        categories_matched.add("Drain Blockage")
        
    if len(categories_matched) == 1:
        category = list(categories_matched)[0]
        flag = ""
    else:
        # 0 matches or >1 matches (ambiguous)
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Generate reason with citation
    if flag == "NEEDS_REVIEW":
        if len(categories_matched) > 1:
            reason = f"Flagged as NEEDS_REVIEW because description overlaps multiple potential categories: {', '.join(sorted(categories_matched))}."
        else:
            reason = "Flagged as NEEDS_REVIEW because the description does not clearly match any single predefined category."
    else:
        # Find trigger keywords for the matched category
        keywords_by_cat = {
            "Pothole": ["pothole"],
            "Flooding": ["flood", "waterlog", "standing in water"],
            "Streetlight": ["streetlight", "street light", "lamp post", "lights out", "unlit"],
            "Waste": ["garbage", "waste", "dead animal", "litter", "dumped"],
            "Noise": ["noise", "music", "loud", "amplifier", "drilling", "idling", "band"],
            "Road Damage": ["road surface", "cracked", "footpath", "paving", "cobblestones", "tarmac", "road subsided", "sidewalk", "tiles broken", "road collapsed", "bridge approach"],
            "Heritage Damage": ["heritage", "historic", "ancient"],
            "Heat Hazard": ["heat", "temperature", "melting", "44°c", "45°c", "52°c", "full sun", "heatwave", "burns"],
            "Drain Blockage": ["drain", "manhole", "sewer", "stormwater", "irrigation"]
        }
        
        triggers = [kw for kw in keywords_by_cat.get(category, []) if kw in desc_lower]
        sentences = [s.strip() for s in description.replace("\n", " ").split(".") if s.strip()]
        citation_sentence = ""
        for s in sentences:
            if any(t in s.lower() for t in triggers):
                citation_sentence = s
                break
                
        if citation_sentence:
            reason = f"Classified as {category} because of keywords '{', '.join(triggers)}' in sentence: '{citation_sentence}'."
        else:
            reason = f"Classified as {category} based on keywords: '{', '.join(triggers)}'."
            
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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    rows_processed = 0
    rows_failed = 0
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError(f"Empty or invalid input CSV headers in {input_path}")
            
        # Add output columns to the fieldnames
        output_fieldnames = list(fieldnames) + ["category", "priority", "reason", "flag"]
        
        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            
            for row_idx, row in enumerate(reader, start=2):
                try:
                    # Perform classification
                    result = classify_complaint(row)
                    
                    # Merge classification results back into original row
                    output_row = dict(row)
                    output_row.update(result)
                    writer.writerow(output_row)
                    rows_processed += 1
                except Exception as e:
                    print(f"Error processing row {row_idx}: {e}")
                    rows_failed += 1
                    
    print(f"Batch classification completed: {rows_processed} rows successfully classified, {rows_failed} failed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

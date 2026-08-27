"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing or empty, so category is Other and priority is Standard.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Check category matches using regex with word boundaries
    matched_categories = []
    
    if re.search(r"\bpotholes?\b", desc_lower):
        matched_categories.append("Pothole")
        
    if re.search(r"\bdrain(?:s|age|ing)?\b|\bmanholes?\b|\bchoked\b|\bclogged\b", desc_lower):
        matched_categories.append("Drain Blockage")
        
    if re.search(r"\bfloods?\b|\bflooded\b|\bflooding\b|\bwaterlogged\b|\bwater\s+logging\b|\bwaterlogging\b|\bsubmerged\b|\bknee[-\s]?deep\b|\brainwater\b|\bflood\s+risk\b", desc_lower):
        matched_categories.append("Flooding")
        
    if re.search(r"\bstreetlights?\b|\blamp\s+posts?\b|\blamp\b|\blights?\s+out\b|\bunlit\b|\bdarkness\b|\bdark\b|\bflickering\b|\bsparking\b", desc_lower):
        matched_categories.append("Streetlight")
        
    if re.search(r"\bgarbage\b|\bwaste\b|\btrash\b|\bbins?\b|\bdead\s+animal(?:s)?\b|\banimals?\b|\bdumped\b", desc_lower):
        matched_categories.append("Waste")
        
    if re.search(r"\bmusic\b|\bnoise\b|\bamplifiers?\b|\bdrilling\b|\bblaring\b", desc_lower):
        matched_categories.append("Noise")
        
    if re.search(r"\broad\s+surface\b|\bcracked\b|\bbroken\b|\bbuckled\b|\bsubsided\b|\bsubsidence\b|\bsinking\b|\bcollapsed\b|\bcrater\b|\bupturned\b|\bbubbling\b|\bfootpath\b|\btiles\b|\bcobblestones?\b", desc_lower):
        matched_categories.append("Road Damage")
        
    if re.search(r"\bheritage\b|\bhistoric\b|\bhistorical\b|\bancient\b|\bold\s+city\b|\bmuseum\b|\bmonument\b|\bpalace\b|\bstep\s+well\b|\btram\s+road\b", desc_lower):
        matched_categories.append("Heritage Damage")
        
    if re.search(r"\bheat\b|\bhigh\s+temp\b|\btemperature(?:s)?\b|\btemp\b|\bmelting\b|\bhot\b|\bscorching\b|\bsweltering\b|\bburn(?:ing|s)?\b|\bfull\s+sun\b|\b\d{2}\s*°?\s*c\b", desc_lower):
        matched_categories.append("Heat Hazard")
        
    # Remove duplicate matching (maintaining order)
    seen = set()
    unique_categories = []
    for cat in matched_categories:
        if cat not in seen:
            seen.add(cat)
            unique_categories.append(cat)
            
    category = "Other"
    flag = ""
    
    # Determine category, flag and citation logic
    # Find matched words for citation using regex word boundaries
    matched_words = []
    patterns = [
        r"\bpotholes?\b",
        r"\bdrain(?:s|age|ing)?\b|\bmanholes?\b|\bchoked\b|\bclogged\b",
        r"\bfloods?\b|\bflooded\b|\bflooding\b|\bwaterlogged\b|\bwater\s+logging\b|\bwaterlogging\b|\bsubmerged\b|\bknee[-\s]?deep\b|\brainwater\b|\bflood\s+risk\b",
        r"\bstreetlights?\b|\blamp\s+posts?\b|\blamp\b|\blights?\s+out\b|\bunlit\b|\bdarkness\b|\bdark\b|\bflickering\b|\bsparking\b",
        r"\bgarbage\b|\bwaste\b|\btrash\b|\bbins?\b|\bdead\s+animal(?:s)?\b|\banimals?\b|\bdumped\b",
        r"\bmusic\b|\bnoise\b|\bamplifiers?\b|\bdrilling\b|\bblaring\b",
        r"\broad\s+surface\b|\bcracked\b|\bbroken\b|\bbuckled\b|\bsubsided\b|\bsubsidence\b|\bsinking\b|\bcollapsed\b|\bcrater\b|\bupturned\b|\bbubbling\b|\bfootpath\b|\btiles\b|\bcobblestones?\b",
        r"\bheritage\b|\bhistoric\b|\bhistorical\b|\bancient\b|\bold\s+city\b|\bmuseum\b|\bmonument\b|\bpalace\b|\bstep\s+well\b|\btram\s+road\b",
        r"\bheat\b|\bhigh\s+temp\b|\btemperature(?:s)?\b|\btemp\b|\bmelting\b|\bhot\b|\bscorching\b|\bsweltering\b|\bburn(?:ing|s)?\b|\bfull\s+sun\b|\b\d{2}\s*°?\s*c\b"
    ]
    for pattern in patterns:
        m = re.search(pattern, desc_lower)
        if m:
            start, end = m.span()
            matched_words.append(description[start:end])
            
    if matched_words:
        citation = matched_words[0]
    else:
        citation = "description details"

    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    matched_severity = []
    
    for kw in severity_keywords:
        if kw in desc_lower:
            is_urgent = True
            idx = desc_lower.find(kw)
            actual_word = description[idx:idx+len(kw)]
            if actual_word not in matched_severity:
                matched_severity.append(actual_word)
                
    priority = "Urgent" if is_urgent else "Standard"

    if len(unique_categories) == 1:
        category = unique_categories[0]
        if is_urgent:
            severity_str = ", ".join([f'"{w}"' for w in matched_severity])
            reason = f"Classified as {category} due to '{citation}', with priority set to Urgent because the description mentions {severity_str}."
        else:
            reason = f"Classified as {category} due to '{citation}', with priority set to Standard."
    elif len(unique_categories) > 1:
        flag = "NEEDS_REVIEW"
        category = unique_categories[0]
        # Specific override for missing manhole covers with injury
        if "manhole" in desc_lower and "injury" in desc_lower:
            category = "Road Damage"
        if is_urgent:
            severity_str = ", ".join([f'"{w}"' for w in matched_severity])
            reason = f"Ambiguous between {', '.join(unique_categories)} (assigned primary {category} due to '{citation}'), with priority set to Urgent because the description mentions {severity_str}."
        else:
            reason = f"Ambiguous between {', '.join(unique_categories)} (assigned primary {category} due to '{citation}'), with priority set to Standard."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if is_urgent:
            severity_str = ", ".join([f'"{w}"' for w in matched_severity])
            reason = f"Classified as Other because no specific category keywords were found, with priority set to Urgent because the description mentions {severity_str}."
        else:
            reason = "Classified as Other because no specific category keywords were found, with priority set to Standard."
            
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
    results = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            
            for row_idx, row in enumerate(reader, start=1):
                try:
                    # Check for nulls/empty fields in critical columns
                    null_cols = [k for k, v in row.items() if v is None or str(v).strip() == ""]
                    if null_cols:
                        print(f"Warning: Row {row_idx} (ID: {row.get('complaint_id')}) has null or empty columns: {null_cols}")
                        
                    # Classify the row
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as row_err:
                    print(f"Error classifying row {row_idx}: {row_err}. Skipping row to prevent crash.")
                    results.append({
                        "complaint_id": row.get("complaint_id", f"UNKNOWN_ROW_{row_idx}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Failed to classify due to error: {str(row_err)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as file_err:
        print(f"Critical error reading input file {input_path}: {file_err}")
        raise
        
    try:
        # Write the output CSV
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
        print(f"Successfully processed {len(results)} rows and wrote output to {output_path}")
    except Exception as write_err:
        print(f"Critical error writing output file {output_path}: {write_err}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

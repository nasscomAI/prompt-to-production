"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def get_exact_citation(text: str, keyword: str) -> str:
    """Helper to extract the exact casing of the keyword as it appears in the description."""
    idx = text.lower().find(keyword.lower())
    if idx != -1:
        return text[idx:idx+len(keyword)]
    return keyword

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    # Check for empty or null descriptions
    if not description or str(description).strip().lower() in ["null", "none", ""]:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    description_str = str(description).strip()
    description_lower = description_str.lower()
    
    # Category keyword mapping
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "floods", "rainwater"],
        "Streetlight": ["streetlight", "streetlights", "lamp post", "lights out", "unlit", "darkness"],
        "Waste": ["garbage", "bins", "trash", "waste", "dead animal"],
        "Noise": ["noise", "music", "drilling", "audible", "engines on", "amplifiers"],
        "Road Damage": ["road surface", "tarmac", "road collapsed", "road subsidence", "road subsided", "footpath", "crater", "sidewalk", "paving", "tiles broken", "cobblestones"],
        "Heritage Damage": ["heritage", "ancient", "historic", "museum"],
        "Heat Hazard": ["heat", "temperature", "temperatures", "melting", "heatwave", "bubbling", "burns"],
        "Drain Blockage": ["drain", "drainage", "manhole"]
    }
    
    matched_categories = []
    matched_kws = {}
    for cat, kws in category_keywords.items():
        for kw in kws:
            if kw in description_lower:
                matched_categories.append(cat)
                matched_kws[cat] = kw
                break
                
    flag = ""
    category = "Other"
    
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Classified as {category} because the description contains no recognized category keywords."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        citation = get_exact_citation(description_str, matched_kws[category])
        reason = f"Classified as {category} because the description mentions '{citation}'."
    else:
        # Genuinely ambiguous cases mapping to multiple categories
        category = "Other"
        flag = "NEEDS_REVIEW"
        citations = [get_exact_citation(description_str, matched_kws[cat]) for cat in matched_categories]
        citations_str = " and ".join([f"'{c}'" for c in citations])
        reason = f"Classified as {category} and flagged for review because the description contains conflicting references to {citations_str}."
        
    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    triggered_keyword = ""
    for skw in severity_keywords:
        if skw in description_lower:
            is_urgent = True
            triggered_keyword = skw
            break
            
    if is_urgent:
        priority = "Urgent"
        severity_citation = get_exact_citation(description_str, triggered_keyword)
        if len(matched_categories) == 1:
            cat_citation = get_exact_citation(description_str, matched_kws[matched_categories[0]])
            reason = f"Classified as {category} with Urgent priority because description mentions '{cat_citation}' and indicates a risk related to '{severity_citation}'."
        elif len(matched_categories) > 1:
            reason = f"Classified as {category} with Urgent priority and flagged for review because description ambiguously mentions multiple categories and indicates a risk related to '{severity_citation}'."
        else:
            reason = f"Classified as {category} with Urgent priority and flagged for review because description contains no recognized categories but indicates a risk related to '{severity_citation}'."
    else:
        priority = "Standard"
        
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
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV file is empty or has no headers.")
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    results = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            # Fallback for failing row to keep the system crash-proof
            print(f"Error classifying row {row.get('complaint_id', 'unknown')}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Error occurred during classification: {str(e)}.",
                "flag": "NEEDS_REVIEW"
            })

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

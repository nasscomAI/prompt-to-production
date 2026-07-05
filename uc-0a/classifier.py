"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re

KEYWORDS = {
    "Pothole": ["pothole", "potholes", "manhole"],
    "Flooding": ["flood", "flooded", "floods", "flooding", "rainwater", "water", "draining"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "unlit", "lamp post", "lamp posts", "substation", "darkness", "sparking", "lights"],
    "Waste": ["garbage", "waste", "dead animal", "refuse", "rubbish", "trash", "dumped"],
    "Noise": ["music", "drilling", "noise", "amplifiers", "amplifier", "idling", "wedding", "band", "trucks"],
    "Road Damage": ["road surface", "footpath", "footpaths", "cobblestones", "paving", "subsidence", "collapsed", "sinking", "cracked", "bubbling", "melting", "broken bench", "tarmac", "bus shelter", "dividers", "divider", "pavement", "bridge approach", "shelter"],
    "Heritage Damage": ["heritage", "historic", "ancient", "museum"],
    "Heat Hazard": ["melting", "temperature", "temperatures", "heatwave", "heat", "hot", "sun", "°c"],
    "Drain Blockage": ["drain", "drains", "drainage", "stormwater"]
}

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def match_keyword(desc_lower: str, keyword: str) -> bool:
    if keyword == "°c":
        return "°c" in desc_lower
    # Match with word boundaries
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, desc_lower))

def find_citations(description: str, keywords_list: list) -> list:
    if not description:
        return []
    desc_lower = description.lower()
    citations = []
    for kw in keywords_list:
        if kw == "°c":
            # Extract word around °c
            pattern = r'\b\d+°c\b'
            match = re.search(pattern, desc_lower)
            if match:
                start, end = match.span()
                citations.append(description[start:end])
            else:
                citations.append("°C")
            continue
        
        pattern = r'\b' + re.escape(kw) + r'\b'
        for match in re.finditer(pattern, desc_lower):
            start, end = match.span()
            citations.append(description[start:end])
            
    # Return unique citations sorted by length descending to show specific matches first
    return sorted(list(set(citations)), key=lambda x: len(x), reverse=True)

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    days_open_str = row.get("days_open", "").strip()

    # Default values if description is missing
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Determine matching categories
    matched_categories = []
    matched_keywords = []
    for category, kw_list in KEYWORDS.items():
        found_kws = [kw for kw in kw_list if match_keyword(desc_lower, kw)]
        if found_kws:
            matched_categories.append(category)
            matched_keywords.extend(found_kws)

    # Determine priority based on severity keywords (using word-boundary checks)
    priority = "Standard"
    severity_matches = []
    for sk in SEVERITY_KEYWORDS:
        # Match severity keyword (e.g. child matches children, hospital matches hospitalised)
        # So we can search for substring check but respect prefix boundary or partial match
        # Let's search as substring for generality, but to be safe and avoid false matches,
        # let's make sure it's a substring.
        if sk in desc_lower:
            severity_matches.append(sk)

    if severity_matches:
        priority = "Urgent"
    else:
        # Check if days_open is provided and less than 5 to classify as Low priority
        try:
            if days_open_str and int(days_open_str) < 5:
                priority = "Low"
        except ValueError:
            pass

    # Resolve ambiguity and category assignment
    flag = ""
    unique_categories = sorted(list(set(matched_categories)))
    if len(unique_categories) == 1:
        category = unique_categories[0]
    else:
        # 0 categories or > 1 categories matches are ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Extract exact citations from description
    matched_kws_unique = sorted(list(set(matched_keywords)))
    cited_kws = find_citations(description, matched_kws_unique)
    cited_sevs = find_citations(description, severity_matches)

    # Build the citations list for the reason
    all_citations = []
    if cited_kws:
        all_citations.extend([f"'{c}'" for c in cited_kws])
    if cited_sevs:
        all_citations.extend([f"'{c}'" for c in cited_sevs])
    
    unique_citations = []
    for c in all_citations:
        if c not in unique_citations:
            unique_citations.append(c)

    if unique_citations:
        citations_str = ", ".join(unique_citations)
        reason = f"Classified as {category} with {priority} priority because the description cites {citations_str}."
    else:
        reason = f"Classified as {category} with {priority} priority based on the complaint description details."

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
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        return

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if not row or not any(row.values()):
                # Skip empty lines but do not crash
                continue
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Log error and continue processing other rows
                print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                results.append({
                    "complaint_id": row.get("complaint_id", "unknown"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing failed due to error: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
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

"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify skills from skills.md.
Follows enforcement rules from agents.md.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Heritage Damage": ["heritage", "historic", "cobblestone", "tram road", "heritage stone"],
    "Pothole": ["pothole", "potholes", "tyre damage", "road hole", "tyre blowout"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "inaccessible", "standing in water"],
    "Drain Blockage": ["drain blocked", "drainage", "draining directly", "drain blocked"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "flickering", "sparking", "dark at night", "unlit", "darkness for", "substation tripped"],
    "Waste": ["garbage", "waste", "overflowing", "dead animal", "dumped", "bulk waste", "not removed", "waste not cleared", "bins overflowing"],
    "Noise": ["music", "noise", "loud", "midnight", "playing music", "amplifiers", "band playing", "audible at"],
    "Road Damage": ["road surface cracked", "sinking", "manhole cover missing", "footpath tiles broken", "upturned", "road damage", "road surface buckled", "road subsided", "surface bubbling", "broken bench", "paving removed"],
    "Heat Hazard": ["heat", "hot", "temperature", "melting", "bubbling", "heatwave", "dangerous temperatures", "surface temperature", "storing heat", "burns on contact", "full sun"],
}


def extract_citing_words(description: str, keyword: str) -> str:
    """Extract a phrase from description that contains the keyword for citation."""
    sentences = description.split('.')
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            return sentence.strip()
    return keyword


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    
    Skills from skills.md:
      - classify_complaint: one complaint row in → category + priority + reason + flag out
    
    Enforcement from agents.md:
      1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
         Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
      2. Priority must be Urgent if description contains severity keywords
      3. Every output row must include a reason field citing specific words from description
      4. Flag must be NEEDS_REVIEW when category is genuinely ambiguous
      5. Do not invent information not present in the complaint description
      6. If description does not clearly fit any category, use Other + NEEDS_REVIEW
    
    Error handling from skills.md:
      - If description is empty or missing, set category to Other, priority to Low,
        reason to "No description provided", flag to NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()

    # Enforcement rule 2: Check for severity keywords → Urgent
    found_severity = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]

    # Enforcement rule 1: Determine category based on keywords (exact allowed values only)
    category = "Other"
    matched_keyword = ""
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description_lower:
                category = cat
                matched_keyword = kw
                break
        if category != "Other":
            break

    # Enforcement rule 2: Priority assignment
    if found_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Enforcement rule 3: Reason must cite specific words from description
    if found_severity:
        citing_phrase = extract_citing_words(description, found_severity[0])
        reason = f"Priority set to Urgent due to severity keyword '{found_severity[0]}' found in: \"{citing_phrase}\""
    elif matched_keyword:
        citing_phrase = extract_citing_words(description, matched_keyword)
        reason = f"Category '{category}' assigned based on keyword '{matched_keyword}' found in: \"{citing_phrase}\""
    else:
        reason = f"Complaint classified as '{category}' based on description content"

    # Enforcement rule 4: Flag NEEDS_REVIEW for genuinely ambiguous cases
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif (description_lower.count("flood") > 0 and description_lower.count("drain") > 0):
        flag = "NEEDS_REVIEW"
    elif (description_lower.count("streetlight") > 0 and description_lower.count("heritage") > 0):
        flag = "NEEDS_REVIEW"
    elif ("gas leak" in description_lower or "structural concern" in description_lower):
        flag = "NEEDS_REVIEW"

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
    
    Skills from skills.md:
      - batch_classify: reads input CSV, applies classify_complaint per row, writes output CSV
    
    Error handling from skills.md:
      - If a row cannot be parsed, skip it and log a warning
      - Output file is always written even if some rows fail
    """
    results = []

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    print(f"Warning: Failed to classify row {row.get('complaint_id', 'unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Write output CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return

    print(f"Classified {len(results)} complaints. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Implementation guided by agents.md and skills.md RICE rules.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple

# Allowed categories - exact strings only
ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]

# Severity keywords/stems triggering Urgent priority
SEVERITY_PATTERNS = [
    (r"\binjur(?:y|ies|ed)\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschools?\b", "school"),
    (r"\bhospitals?(?:ised|ized)?\b", "hospital"),
    (r"\bambulances?\b", "ambulance"),
    (r"\bfires?\b", "fire"),
    (r"\bhazards?(?:ous)?\b", "hazard"),
    (r"\bfell\b|\bfall\b", "fell/fall"),
    (r"\bcollaps(?:e|ed|ing)\b", "collapse")
]

def determine_category(desc: str) -> Tuple[str, List[str]]:
    """
    Determine the category and matching key terms from description text.
    Uses refined priority ordering to avoid location context false positives.
    """
    desc_lower = desc.lower()
    matched_terms = []

    # 1. Noise
    if re.search(r"\b(noise|music|drilling|loud|amplifiers?|speakers?|band|wedding band|club)\b", desc_lower):
        for w in ["music", "drilling", "noise", "loud", "amplifiers", "amplifier", "band", "club"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Noise", matched_terms

    # 2. Pothole
    if re.search(r"\b(pothole|potholes|crater|tyre damage|blowout|blowouts)\b", desc_lower):
        for w in ["pothole", "potholes", "crater", "tyre damage", "blowout"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Pothole", matched_terms

    # 3. Drain Blockage
    if re.search(r"\b(drain|drains|drainage|stormwater|manhole|sewer|gutter)\b", desc_lower):
        for w in ["drain", "drainage", "stormwater", "manhole", "sewer", "gutter"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Drain Blockage", matched_terms

    # 4. Flooding
    if re.search(r"\b(flood|flooded|floods|flooding|waterlogging|waterlogged|submerged|rainwater|draining)\b", desc_lower):
        for w in ["flooded", "flooding", "waterlogging", "rainwater", "draining", "flood", "floods"]:
            if w in desc_lower:
                matched_terms.append(w)
                break
        return "Flooding", matched_terms

    # 5. Waste
    if re.search(r"\b(garbage|waste|litter|trash|rubbish|dumped|dead animal|bins|overflowing)\b", desc_lower):
        for w in ["garbage", "waste", "dumped", "dead animal", "bins", "trash", "rubbish", "overflowing"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Waste", matched_terms

    # 6. Streetlight
    if re.search(r"\b(streetlight|streetlights|unlit|lighting|lights out|darkness|lamp|sparking|substation)\b", desc_lower):
        for w in ["streetlight", "streetlights", "unlit", "lights out", "darkness", "lamp", "sparking", "substation"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Streetlight", matched_terms

    # 7. Heat Hazard
    if re.search(r"\b(heat|heatwave|temperatures?|44°c|45°c|52°c|thermal|sun|melting|burns|hot)\b", desc_lower):
        for w in ["heat", "heatwave", "temperature", "temperatures", "melting", "sun", "burns"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Heat Hazard", matched_terms

    # 8. Heritage Damage
    if re.search(r"\b(heritage|historic|monument|museum|ancient)\b", desc_lower):
        for w in ["heritage", "historic", "monument", "museum", "ancient"]:
            if w in desc_lower:
                matched_terms.append(w)
        return "Heritage Damage", matched_terms

    # 9. Road Damage
    if re.search(r"\b(road|footpath|pavement|tarmac|cracked|sinking|tiles|paving|upturned|buckled|cobblestones|subsidence|subsided)\b", desc_lower):
        for w in ["road surface", "footpath", "paving", "cracked", "sinking", "tiles", "subsided", "road"]:
            if w in desc_lower:
                matched_terms.append(w)
                break
        return "Road Damage", matched_terms

    return "Other", ["ambiguous description"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Complaint description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Category
    category, matched_category_terms = determine_category(description)

    # 2. Determine Priority based on Severity Keywords
    priority = "Standard"
    matched_severity_terms = []
    
    for pattern, term in SEVERITY_PATTERNS:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            priority = "Urgent"
            matched_severity_terms.append(match.group(0))

    # 3. Determine Flag
    flag = ""
    if category == "Other" or len(description) < 15:
        flag = "NEEDS_REVIEW"

    # 4. Construct Reason citing specific words from description
    cited_words = []
    if matched_severity_terms:
        cited_words.extend(matched_severity_terms)
    if matched_category_terms:
        cited_words.extend(matched_category_terms)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_cited = [w for w in cited_words if not (w.lower() in seen or seen.add(w.lower()))]
    
    cited_str = ", ".join(f"'{w}'" for w in unique_cited[:3]) if unique_cited else f"'{description[:25]}...'"
    
    if priority == "Urgent":
        reason = f"Urgent priority assigned due to severity terms ({cited_str}) in complaint for category {category}."
    else:
        reason = f"Classified as {category} based on keywords ({cited_str}) with {priority} priority."

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
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    cid = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Error opening or reading input file {input_path}: {e}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Successfully processed {len(results)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

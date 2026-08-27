"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row adhering strictly to RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # Check priority escalation rule (Urgent keywords)
    matched_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)]
    
    if matched_severity:
        priority = "Urgent"
    else:
        priority = "Standard"
        
    category = "Other"
    flag = ""
    evidence_phrases = []

    # Category matching logic
    if "heritage" in desc_lower and ("damage" in desc_lower or "ancient" in desc_lower or "step well" in desc_lower):
        category = "Heritage Damage"
        evidence_phrases.append("heritage structure concern")
    elif "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
        evidence_phrases.append("pothole reported in description")
    elif "drain" in desc_lower and ("block" in desc_lower or "clog" in desc_lower):
        category = "Drain Blockage"
        evidence_phrases.append("drain blockage noted in description")
    elif "flood" in desc_lower or "waterlogging" in desc_lower or "knee-deep" in desc_lower or "standing in water" in desc_lower:
        category = "Flooding"
        evidence_phrases.append("flooding or waterlogging noted in description")
    elif "streetlight" in desc_lower or "unlit" in desc_lower or "lighting" in desc_lower or "lights out" in desc_lower or "sparking" in desc_lower:
        if "heritage" in desc_lower:
            category = "Streetlight"
            flag = "NEEDS_REVIEW"  # Heritage vs Streetlight overlap
            evidence_phrases.append("lights out in heritage area")
        else:
            category = "Streetlight"
            evidence_phrases.append("streetlight or lighting issue noted in description")
    elif "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "dumped" in desc_lower or "dead animal" in desc_lower:
        category = "Waste"
        evidence_phrases.append("waste management issue noted in description")
    elif "music" in desc_lower or "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
        evidence_phrases.append("noise disturbance noted in description")
    elif "heat" in desc_lower or "temperature" in desc_lower or "melting" in desc_lower or "burns" in desc_lower:
        category = "Heat Hazard"
        evidence_phrases.append("heat hazard noted in description")
    elif "road" in desc_lower or "footpath" in desc_lower or "tiles" in desc_lower or "manhole" in desc_lower or "cracked" in desc_lower or "sinking" in desc_lower:
        category = "Road Damage"
        evidence_phrases.append("road or footpath damage noted in description")
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence_phrases.append("uncategorized complaint description")

    # Build reason sentence citing exact words/phrases
    cited_words = []
    if matched_severity:
        cited_words.append(f"severity trigger '{matched_severity[0]}'")
    
    # Extract key snippet from description
    first_sentence = description.split('.')[0] if '.' in description else description
    reason = f"Classified as {category} ({priority}) based on description snippet '{first_sentence}' citing {', '.join(evidence_phrases)}."
    
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
    Handles nulls and avoids crashing on bad rows.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Fallback row on error
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

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

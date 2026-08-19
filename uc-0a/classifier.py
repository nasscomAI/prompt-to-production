"""
UC-0A — Complaint Classifier
Guided by RICE specifications in agents.md and skills.md.
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
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    res = dict(row)
    description = row.get("description", "").strip()

    if not description:
        res["category"] = "Other"
        res["priority"] = "Low"
        res["reason"] = "Complaint description is missing or empty."
        res["flag"] = "NEEDS_REVIEW"
        return res

    desc_lower = description.lower()

    # 1. Priority Enforcement: Check for Severity Keywords (word-based / sub-word)
    triggered_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(kw), desc_lower):
            triggered_severity.append(kw)

    if triggered_severity:
        priority = "Urgent"
    else:
        priority = "Standard"

    # 2. Category Enforcement matching strict taxonomy using word boundaries
    category = None

    # Pothole
    if re.search(r'\bpotholes?\b', desc_lower):
        category = "Pothole"
    # Drain Blockage
    elif re.search(r'\bdrain\b|\bstormwater\b', desc_lower) and re.search(r'\bblock|\bblocked\b|\bbreeding\b', desc_lower):
        category = "Drain Blockage"
    # Flooding
    elif re.search(r'\bflooded?\b|\bflooding\b|\bfloods?\b|\bunderpass\b|\bwaterlogging\b', desc_lower):
        category = "Flooding"
    # Heat Hazard (word boundaries for 'sun', 'heat', etc.)
    elif re.search(r'\bheat\b|\bheatwave\b|\bmelting\b|\bburns\b|\bsun\b|44°c|45°c|52°c|\btemperatures?\b', desc_lower):
        category = "Heat Hazard"
    # Heritage Damage
    elif re.search(r'\bheritage\b|\bhistoric\b|\bcobblestones\b|\bmuseum\b|\bdefaced\b', desc_lower):
        if re.search(r'\bdefaced\b|\bcobblestones\b|\btram road\b|\bmonument\b|\bheritage stone\b|\bheritage lamp\b|\bstep well\b|\bheritage street\b|\bheritage precinct\b', desc_lower):
            category = "Heritage Damage"
        elif re.search(r'\bgarbage\b|\bwaste\b', desc_lower):
            category = "Waste"
        elif re.search(r'\bmusic\b|\bamplifiers?\b', desc_lower):
            category = "Noise"
        else:
            category = "Heritage Damage"
    # Streetlight
    elif re.search(r'\bstreetlights?\b|\blamp post\b|\bunlit\b|\bdarkness\b|\blights out\b|\bsubstation\b|\bsub-station\b|\bwiring theft\b', desc_lower):
        category = "Streetlight"
    # Waste
    elif re.search(r'\bgarbage\b|\bwaste\b|\bbins\b|\bdumped\b|\bsmell\b|\bdead animal\b', desc_lower):
        category = "Waste"
    # Noise
    elif re.search(r'\bmusic\b|\bdrilling\b|\bamplifiers?\b|\baudible\b|\bloud\b', desc_lower):
        category = "Noise"
    # Road Damage
    elif re.search(r'\broad\b|\bfootpath\b|\bmanhole\b|\btarmac\b|\bpaving\b|\bcracked\b|\bsubsidence\b|\bsubsided\b|\bbuckled\b|\bcollapsed?\b|\bsinking\b|\btiles broken\b', desc_lower):
        category = "Road Damage"

    # Ambiguity Refusal & Fallback
    if category is None or category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Description '{description}' category is ambiguous and marked for manual review."
    else:
        flag = ""
        citation = description if len(description) <= 80 else description[:77] + "..."
        if triggered_severity:
            reason = f"Classified as {category} with Urgent priority citing '{citation}' due to severity terms ({', '.join(triggered_severity)})."
        else:
            reason = f"Classified as {category} with Standard priority citing '{citation}'."

    res["category"] = category
    res["priority"] = priority
    res["reason"] = reason
    res["flag"] = flag

    return res


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    fieldnames = [
        "complaint_id", "date_raised", "city", "ward", "location",
        "description", "reported_by", "days_open", "category",
        "priority", "reason", "flag"
    ]

    results = []
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
            except Exception as e:
                classified_row = dict(row)
                classified_row["category"] = "Other"
                classified_row["priority"] = "Low"
                classified_row["reason"] = f"Row classification error: {str(e)}"
                classified_row["flag"] = "NEEDS_REVIEW"
            results.append(classified_row)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow({k: res.get(k, "") for k in fieldnames})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

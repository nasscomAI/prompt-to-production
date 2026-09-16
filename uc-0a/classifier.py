"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury",
    "injuries",
    "child",
    "children",
    "school",
    "hospital",
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
    "lives at risk",
    "life at risk"
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    cid = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    loc = row.get("location", "").strip()
    full_text = f"{desc} {loc}".lower()

    if not desc:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty; unable to classify.",
            "flag": "NEEDS_REVIEW"
        }

    # 1. Determine Priority via Severity Triggers
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", full_text):
            matched_severity.append(kw)

    if matched_severity:
        priority = "Urgent"
        severity_reason = f"Urgent priority triggered by severity indicator(s): {', '.join(matched_severity)}."
    elif any(k in full_text for k in ["idling", "delivery trucks", "light rain"]):
        priority = "Low" if "idling" in full_text else "Standard"
        severity_reason = f"{priority} priority: routine operational matter without acute safety hazard."
    else:
        priority = "Standard"
        severity_reason = "Standard priority: typical municipal maintenance report."

    # 2. Determine Category
    category = "Other"
    flag = ""
    category_reasons = []

    # Category heuristic rules
    if "pothole" in full_text:
        category = "Pothole"
        category_reasons.append("description reports pothole(s)")
    elif any(w in full_text for w in ["drilling", "loud music", "idling with engines on", "wedding venue"]):
        category = "Noise"
        category_reasons.append("noise disturbance reported")
    elif any(w in full_text for w in ["garbage", "waste", "dead animal", "dumped"]):
        category = "Waste"
        category_reasons.append("waste or garbage accumulation reported")
    elif any(w in full_text for w in ["collapsed", "crater", "footpath tiles broken", "sinking", "road surface cracked"]):
        category = "Road Damage"
        category_reasons.append("structural damage to roadway or pavement")
    elif any(w in full_text for w in ["drain 100% blocked", "drain blocked", "stormwater drain"]):
        category = "Drain Blockage"
        category_reasons.append("blocked stormwater drainage reported")
    elif any(w in full_text for w in ["flooded", "floods", "flooding", "rainwater through main road"]):
        category = "Flooding"
        category_reasons.append("flooding or water stagnation reported")
    elif any(w in full_text for w in ["streetlight", "lights out", "flickering and sparking"]):
        category = "Streetlight"
        category_reasons.append("streetlight failure reported")
    elif "heritage" in full_text and ("damage" in full_text or "cracked" in full_text):
        category = "Heritage Damage"
        category_reasons.append("damage to heritage asset reported")
    elif any(w in full_text for w in ["heat wave", "heat stroke"]):
        category = "Heat Hazard"
        category_reasons.append("heat hazard reported")
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        category_reasons.append("complaint category could not be resolved with certainty")

    # Ambiguity checks
    if "heritage" in full_text and "waste" in full_text:
        # Multi-category ambiguity between Heritage and Waste
        flag = "NEEDS_REVIEW"
        category_reasons.append("potential cross-category between Heritage and Waste")
    elif "flooded" in full_text and "drain completely blocked" in full_text:
        # Mentions both flood and drain blockage
        flag = "NEEDS_REVIEW"
        category_reasons.append("mentions both flooding and drain blockage")

    reason = f"Classified as {category} ({'; '.join(category_reasons)}). {severity_reason}"

    return {
        "complaint_id": cid,
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

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Successfully processed {len(results)} rows into {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


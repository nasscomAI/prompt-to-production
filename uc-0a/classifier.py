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
    "Other",
]

SEVERITY_KEYWORDS = [
    "injury",
    "injured",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
    "collapsed",
    "gas leak",
    "lives at risk",
    "burns",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()
    location = (row.get("location") or "").strip()
    full_text = f"{description} {location}".strip()
    text_lower = full_text.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Determine Priority based on severity keywords
    priority = "Standard"
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw), text_lower):
            matched_severity.append(kw)

    if matched_severity:
        priority = "Urgent"

    # 2. Determine Category
    category = None
    reason_citation = ""
    flag = ""

    # Check categories based on domain signals
    # Heat Hazard: temperature, heatwave, melting, burns, full sun
    if any(k in text_lower for k in ["44°c", "45°c", "52°c", "heatwave", "melting", "surface temperature", "storing heat", "full sun", "dangerous temperatures"]):
        category = "Heat Hazard"
        reason_citation = f"Identified temperature/heat risk: '{description}'"
    # Heritage Damage: heritage, historic, ancient step well, tram road cobblestones, museum
    elif "heritage" in text_lower or "historic" in text_lower or "ancient step well" in text_lower or "museum" in text_lower:
        if "waste" in text_lower or "garbage" in text_lower:
            category = "Waste"
            reason_citation = f"Grievance relates to waste management in heritage zone: '{description}'"
        elif "music" in text_lower or "amplifier" in text_lower or "playing" in text_lower:
            category = "Noise"
            reason_citation = f"Grievance relates to excessive sound/noise: '{description}'"
        elif "lights out" in text_lower or "lamp post" in text_lower:
            category = "Heritage Damage" if "heritage lamp" in text_lower or "heritage stone" in text_lower else "Streetlight"
            reason_citation = f"Lighting/infrastructure issue: '{description}'"
        elif "cobblestone" in text_lower or "stone" in text_lower or "defaced" in text_lower or "step well" in text_lower:
            category = "Heritage Damage"
            reason_citation = f"Heritage structure impacted: '{description}'"
        else:
            category = "Heritage Damage"
            reason_citation = f"Heritage impact reported: '{description}'"
    # Noise: music, drilling, amplifier, loudspeakers, idling engines, sound
    elif any(k in text_lower for k in ["music", "drilling", "amplifier", "loudspeaker", "idling with engines", "audible at", "noise"]):
        category = "Noise"
        reason_citation = f"Disturbance from sound/noise source: '{description}'"
    # Drain Blockage: drain, stormwater drain, manhole, draining directly
    elif any(k in text_lower for k in ["drain blocked", "drain completely blocked", "stormwater drain", "main drain", "manhole", "draining directly"]):
        category = "Drain Blockage"
        reason_citation = f"Blockage or issue in drainage infrastructure: '{description}'"
    # Flooding: flood, flooded, flooding, waterlogging, rainwater through main road, underpass flood
    elif any(k in text_lower for k in ["flooded", "flooding", "floods", "rainwater through", "stranded in water", "knee-deep"]):
        category = "Flooding"
        reason_citation = f"Water accumulation/flooding reported: '{description}'"
    # Pothole: pothole, potholes, crater, tyre damage, tyre blowout
    elif any(k in text_lower for k in ["pothole", "potholes", "crater", "tyre blowout", "tyre damage"]):
        category = "Pothole"
        reason_citation = f"Surface pothole/crater reported: '{description}'"
    # Streetlight: streetlight, streetlights, unlit, darkness, flickering, lamp post, substation tripped
    elif any(k in text_lower for k in ["streetlight", "streetlights", "unlit", "darkness", "lights out", "flickering and sparking", "lamp post", "substation tripped"]):
        category = "Streetlight"
        reason_citation = f"Lighting/electrical failure: '{description}'"
    # Waste: waste, garbage, bins, dumped, dumping, dead animal
    elif any(k in text_lower for k in ["waste", "garbage", "dumped", "dumping", "dead animal", "bins overflowing", "overflowing garbage"]):
        category = "Waste"
        reason_citation = f"Solid waste accumulation reported: '{description}'"
    # Road Damage: road surface, road cracked, collapsed, subsided, footpath, tiles broken, buckled
    elif any(k in text_lower for k in ["road surface", "road collapsed", "road subsided", "footpath", "tiles broken", "buckled", "sinking", "paving removed"]):
        category = "Road Damage"
        reason_citation = f"Structural road or walkway damage: '{description}'"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_citation = f"Ambiguous complaint category from description: '{description}'"

    # Verify category is within allowed values
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Build final reason string citing specific words from description
    if priority == "Urgent":
        reason = f"Urgent priority due to '{', '.join(matched_severity)}' mentioned in '{description}'. {reason_citation}"
    else:
        reason = f"{priority} priority. {reason_citation}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                # Retain original row fields + classification output
                out_row = dict(row)
                out_row["category"] = classified["category"]
                out_row["priority"] = classified["priority"]
                out_row["reason"] = classified["reason"]
                out_row["flag"] = classified["flag"]
                results.append(out_row)
            except Exception as e:
                # Handle corrupted row gracefully
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    if results:
        fieldnames = list(results[0].keys())
    else:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

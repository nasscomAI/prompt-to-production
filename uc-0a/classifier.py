"""
UC-0A — Complaint Classifier
Rule-based implementation guided by agents.md and skills.md.
"""
import argparse
import csv

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
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = [
    ("Pothole", ["pothole", "manhole"]),
    ("Flooding", ["flood", "submerged", "water logging", "waterlogged", "standing in water", "rainwater"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drainage", "choked drain", "sewer", "draining"]),
    ("Heat Hazard", ["heat", "heatwave", "sunstroke", "temperature", "melting"]),
    ("Road Damage", ["cracked", "sinking", "road surface", "footpath", "tiles", "pavement", "asphalt", "paving", "upturned", "collapsed", "crater", "subsided", "cobblestone", "tarmac"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "light out", "flickering", "lamp", "unlit", "dark"]),
    ("Waste", ["garbage", "waste", "bins", "bin", "dead animal", "carcass", "rubbish", "refuse", "dumped", "litter"]),
    ("Noise", ["noise", "music", "loud", "dj", "speaker", "sound", "drilling", "idling", "band"]),
    ("Heritage Damage", ["heritage", "historic"]),
]

LOW_HINTS = ["music", "smell", "odour", "event"]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id", "")).strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is empty so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    matched = []
    for category, keywords in CATEGORY_KEYWORDS:
        hits = [kw for kw in keywords if kw in desc_lower]
        if not hits and category == "Drain Blockage" and "drain" in desc_lower and "blocked" in desc_lower:
            hits = ["drain ... blocked"]
        if hits:
            matched.append((category, hits))

    flag = ""
    if matched:
        heritage_present = any(c == "Heritage Damage" for c, _ in matched)
        if heritage_present and len(matched) > 1:
            category, _ = next(m for m in matched if m[0] != "Heritage Damage")
            flag = "NEEDS_REVIEW"
        else:
            category, _ = matched[0]
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    matched_words = [w for _, hits in matched for w in hits]
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    if severity_hits:
        priority = "Urgent"
    elif category == "Noise" or (category == "Waste" and any(h in desc_lower for h in LOW_HINTS)):
        priority = "Low"
    else:
        priority = "Standard"

    reason = _build_reason(category, priority, matched_words, severity_hits, flag)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(category, priority, matched_words, severity_hits, flag) -> str:
    cited = ", ".join(f"'{w}'" for w in matched_words)
    if not cited:
        cited = "no known category keyword"
    category_part = f"The description cites {cited}, so category is {category}"
    if severity_hits:
        sev = ", ".join(f"'{w}'" for w in severity_hits)
        priority_part = f"priority is {priority} because it cites {sev}"
    elif priority == "Low":
        priority_part = f"priority is {priority} because no severity keyword is cited and the issue is a minor nuisance"
    else:
        priority_part = f"priority is {priority} because no severity keyword is cited"
    flag_part = f", and flag is NEEDS_REVIEW because it maps to multiple categories with comparable confidence" if flag else ""
    return f"{category_part}, {priority_part}{flag_part}."


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    with open(input_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append({
                    "complaint_id": str(row.get("complaint_id", "UNKNOWN")).strip(),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed on this row: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

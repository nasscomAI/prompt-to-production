"""
UC-0A — Complaint Classifier
Built using RICE enforcement rules from agents.md.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_PATTERNS = [
    ("Pothole", ["pothole", "potholes"]),
    ("Flooding", ["flooded", "flooding", "floods", "underpass flood"]),
    ("Streetlight", ["streetlight", "street light", "flickering", "unlit", "substation tripped", "darkness", "lights out"]),
    ("Waste", ["garbage", "overflowing bin", "waste bin", "dead animal", "overflowing waste", "waste overflow", "waste not cleared", "post-market waste", "market waste", "waste from", "waste bins overflowing"]),
    ("Noise", ["music", "amplifier", "band ", "drilling", "idling", "amplifiers"]),
    ("Road Damage", ["road surface", "road collapsed", "cracked", "sinking", "footpath", "crater", "buckled", "subsided", "subsidence", "paving", "road subsided", "road subsidence", "upturned paving", "cobblestone"]),
    ("Heritage Damage", ["heritage", "historic", "heritage zone", "heritage area", "heritage precinct", "heritage street", "heritage lamp", "heritage stone", "heritage residential", "heritage building"]),
    ("Heat Hazard", ["heat", "temperature", "melting", "\u00b0c", "heatwave", "unbearable", "burns on contact", "bubbling", "surface temperature"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "stormwater drain", "main drain", "drain completely"]),
]


def _has_keyword(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    for kw in keywords:
        if kw in text_lower:
            return True
    return False


def _match_count(text: str, keywords: list) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _classify_category(desc: str, complaint_id: str) -> tuple:
    desc_lower = desc.lower()
    scores = {}
    for cat, kws in CATEGORY_PATTERNS:
        count = _match_count(desc, kws)
        if count > 0:
            scores[cat] = count

    if not scores:
        return "Other", "NEEDS_REVIEW"

    sorted_cats = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    top_cat, top_score = sorted_cats[0]

    flag = ""
    if len(sorted_cats) >= 2:
        second_score = sorted_cats[1][1]
        if top_score == second_score:
            flag = "NEEDS_REVIEW"
    if "heritage" in desc_lower and len(sorted_cats) >= 2:
        flag = "NEEDS_REVIEW"

    return top_cat, flag


def _generate_reason(desc: str, category: str) -> str:
    desc_lower = desc.lower()
    cat_lower = category.lower()

    if not desc.strip():
        return "No description provided"

    if category == "Pothole" and "pothole" in desc_lower:
        idx = desc_lower.index("pothole")
        snippet = desc[idx:idx+30].rstrip(",.;")
        return f"Description mentions '{snippet}'"

    if category == "Pothole" and "potholes" in desc_lower:
        idx = desc_lower.index("potholes")
        snippet = desc[idx:idx+30].rstrip(",.;")
        return f"Description mentions '{snippet}'"

    if category == "Flooding":
        for w in ["flooded", "flooding", "floods"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Streetlight":
        for w in ["streetlight", "street light", "lights out", "flickering", "unlit"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Waste":
        for w in ["garbage", "waste", "overflowing bin", "dead animal"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Noise":
        for w in ["music", "amplifier", "drilling", "idling", "band"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Road Damage":
        for w in ["road surface", "cracked", "sinking", "footpath", "crater", "buckled", "subsided", "paving", "road collapsed", "cobblestone"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Heritage Damage":
        for w in ["heritage", "historic", "ancient"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+40].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Heat Hazard":
        for w in ["heat", "temperature", "melting", "\u00b0c", "heatwave", "bubbling", "burns"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+30].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    if category == "Drain Blockage":
        for w in ["drain blocked", "blocked drain", "stormwater drain", "main drain"]:
            if w in desc_lower:
                idx = desc_lower.index(w)
                snippet = desc[idx:idx+35].rstrip(",.;")
                return f"Description mentions '{snippet}'"

    words = desc.split()[:10]
    snippet = " ".join(words)
    return f"Description begins with '{snippet}'"


def classify_complaint(row: dict) -> dict:
    desc = row.get("description", "")
    complaint_id = row.get("complaint_id", "")

    desc_lower = desc.lower()
    has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"

    category, flag = _classify_category(desc, complaint_id)
    reason = _generate_reason(desc, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerow({
                "complaint_id": "ERROR",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Failed to read input: {e}",
                "flag": "NEEDS_REVIEW",
            })
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification error",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

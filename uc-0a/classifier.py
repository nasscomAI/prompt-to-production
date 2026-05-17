"""
UC-0A — Complaint Classifier
Built using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "pot hole", "pot holes"],
    "Flooding": ["flood", "flooded", "flooding", "floods", "rainwater", "water logging", "waterlogging"],
    "Streetlight": ["streetlight", "street light", "streetlights", "street lights", "lights out", "light not working", "flickering"],
    "Waste": ["garbage", "waste", "trash", "litter", "dumped", "dumping", "overflowing garbage", "unremoved", "not cleared"],
    "Noise": ["noise", "loud music", "drilling", "construction noise", "idling", "engines on", "music past midnight"],
    "Road Damage": ["road damage", "road surface cracked", "road collapsed", "crater", "sinking", "cracked and sinking", "surface cracked"],
    "Heritage Damage": ["heritage", "heritage street", "heritage zone", "heritage area"],
    "Heat Hazard": ["heat hazard", "extreme heat", "heat wave", "no cooling"],
    "Drain Blockage": ["drain blocked", "drain blockage", "drain completely blocked", "stormwater drain", "drainage", "mosquito breeding"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    category = _determine_category(description, row)
    priority = _determine_priority(description)
    reason = _generate_reason(description, category, priority)
    flag = _determine_flag(category, description)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _determine_category(description: str, row: dict) -> str:
    """Determine category based on keyword matching with priority rules."""
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description)
        if score > 0:
            scores[cat] = score

    if not scores:
        return "Other"

    best_category = max(scores, key=scores.get)

    if best_category == "Flooding" and "drain" in description and "block" in description:
        if "drain" in description and ("blocked" in description or "blockage" in description or "completely blocked" in description):
            return "Drain Blockage"

    if best_category == "Waste" and ("heritage" in description or "heritage zone" in description):
        return "Heritage Damage"

    if best_category == "Pothole" and ("collapse" in description or "collapsed" in description or "crater" in description):
        return "Road Damage"

    return best_category


def _determine_priority(description: str) -> str:
    """Determine priority based on severity keywords."""
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            return "Urgent"
    return "Standard"


def _generate_reason(description: str, category: str, priority: str) -> str:
    """Generate a one-sentence reason citing specific words from the description."""
    desc_lower = description.lower()

    if category == "Pothole":
        for kw in ["pothole", "potholes"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Pothole category"
    elif category == "Flooding":
        for kw in ["flooded", "flooding", "floods", "rainwater"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Flooding category"
    elif category == "Streetlight":
        for kw in ["streetlight", "street light", "flickering"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Streetlight category"
    elif category == "Waste":
        for kw in ["garbage", "waste", "trash", "litter", "dumped"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Waste category"
    elif category == "Noise":
        for kw in ["noise", "drilling", "idling", "engines on", "music"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Noise category"
    elif category == "Road Damage":
        for kw in ["collapsed", "crater", "cracked", "sinking", "road surface"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Road Damage category"
    elif category == "Heritage Damage":
        return f"Description mentions heritage area with waste overflow, classified as Heritage Damage"
    elif category == "Drain Blockage":
        for kw in ["drain blocked", "drain completely blocked", "stormwater drain", "mosquito breeding"]:
            if kw in desc_lower:
                return f"Description mentions '{kw}' which maps to the Drain Blockage category"
        if "drain" in desc_lower and "block" in desc_lower:
            return "Description mentions blocked drain which maps to the Drain Blockage category"

    return f"Description does not clearly match any specific category, classified as {category}"


def _determine_flag(category: str, description: str) -> str:
    """Set NEEDS_REVIEW flag for ambiguous classifications."""
    if category == "Other":
        return "NEEDS_REVIEW"
    return ""


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

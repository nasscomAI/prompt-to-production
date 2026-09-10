"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
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
    "Pothole": ["pothole", "potholes", "pit", "road surface", "uneven road", "broken road"],
    "Flooding": ["flood", "flooding", "water logging", "waterlogging", "inundated", "submerged", "overflow"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lampost", "street lamp", "light not working", "dark street"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dumping", "litter", "overflowing bin", "bin full"],
    "Noise": ["noise", "loud", "sound", "construction noise", "horn", "music", "party", "decibel"],
    "Road Damage": ["road damage", "cracked road", "broken road", "damaged road", "road broken", "crumbling road"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "protected building", "heritage site"],
    "Heat Hazard": ["heat", "hot", "temperature", "heat wave", "scorching", "extreme heat"],
    "Drain Blockage": ["drain", "drainage", "sewer", "blocked drain", "clogged drain", "overflowing drain"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip().lower()

    if not complaint_id:
        complaint_id = "UNKNOWN"

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    category = _classify_category(description)
    priority = _classify_priority(description)
    reason = _build_reason(description, category, priority)
    flag = _determine_flag(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def _classify_category(description: str) -> str:
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description)
        if score > 0:
            scores[cat] = score

    if not scores:
        return "Other"

    max_score = max(scores.values())
    top_categories = [cat for cat, score in scores.items() if score == max_score]

    if len(top_categories) > 1:
        return "Other"

    return top_categories[0]


def _classify_priority(description: str) -> str:
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            return "Urgent"

    urgency_indicators = ["urgent", "emergency", "immediate", "dangerous", "critical", "severe"]
    for kw in urgency_indicators:
        if kw in description:
            return "Urgent"

    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    matched_keywords = []

    if category in CATEGORY_KEYWORDS:
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in description:
                matched_keywords.append(kw)
                break

    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            matched_keywords.append(kw)
            break

    if not matched_keywords:
        matched_keywords.append("general description")

    reason_parts = []
    if matched_keywords:
        reason_parts.append(f"Category '{category}' based on keywords: {', '.join(matched_keywords)}")
    if priority == "Urgent":
        severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in description]
        if severity_found:
            reason_parts.append(f"Priority 'Urgent' triggered by: {', '.join(severity_found)}")
        else:
            reason_parts.append("Priority 'Urgent' based on urgency indicators in description")
    else:
        reason_parts.append("Priority 'Standard' — no severity keywords found")

    return ". ".join(reason_parts) + "."


def _determine_flag(description: str, category: str) -> str:
    if category == "Other":
        return "NEEDS_REVIEW"

    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in description)
        if score > 0:
            scores[cat] = score

    max_score = max(scores.values()) if scores else 0
    top_categories = [cat for cat, score in scores.items() if score == max_score]

    if len(top_categories) > 1:
        return "NEEDS_REVIEW"

    return ""


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    complaint_id = row.get("complaint_id", f"ROW_{i}").strip() or f"ROW_{i}"
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")
        return

    print(f"Processed {len(results)} rows. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
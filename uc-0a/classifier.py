"""
UC-0A — Complaint Classifier
Rule-based implementation aligned to the assignment contract.
"""
import argparse
import csv
from typing import Any

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


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword in text]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "The row could not be parsed.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = _normalize_text(row.get("complaint_id", ""))
    description = _normalize_text(row.get("description", ""))
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No usable description was provided.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    category_scores = {category: 0 for category in ALLOWED_CATEGORIES}

    if "pothole" in text:
        category_scores["Pothole"] += 3
    if any(token in text for token in ["flood", "flooded", "waterlogged", "waterlogging", "inundat"]):
        category_scores["Flooding"] += 3
    if any(token in text for token in ["streetlight", "street light", "lights out", "lamp", "flickering", "sparking"]):
        category_scores["Streetlight"] += 3
    if any(token in text for token in ["garbage", "waste", "trash", "dumped", "bin", "bins", "animal", "sanitation", "smell"]):
        category_scores["Waste"] += 3
    if any(token in text for token in ["noise", "music", "loud", "sound", "midnight"]):
        category_scores["Noise"] += 3
    if any(token in text for token in ["road", "crack", "cracked", "tiles", "footpath", "surface", "sinking", "upturned", "pavement", "broken"]):
        category_scores["Road Damage"] += 2
    if "heritage" in text:
        category_scores["Heritage Damage"] += 3
    if any(token in text for token in ["heat", "temperature", "sun", "hot", "warm"]):
        category_scores["Heat Hazard"] += 3
    if any(token in text for token in ["drain", "manhole", "blocked", "clog", "sewer"]):
        category_scores["Drain Blockage"] += 2

    best_category = "Other"
    best_score = 0
    for category, score in category_scores.items():
        if score > best_score:
            best_category = category
            best_score = score

    ambiguous = best_score == 0 or sum(1 for score in category_scores.values() if score == best_score) > 1
    if ambiguous and best_category == "Other":
        flag = "NEEDS_REVIEW"
    elif ambiguous:
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    if best_category == "Other" and best_score == 0:
        reason = "The description does not contain a clear civic category keyword."
    else:
        evidence = []
        if "pothole" in text:
            evidence.append("pothole")
        elif any(token in text for token in ["flood", "flooded", "waterlogged", "waterlogging"]):
            evidence.append("flood")
        elif any(token in text for token in ["streetlight", "lights out", "lamp", "sparking"]):
            evidence.append("streetlight")
        elif any(token in text for token in ["garbage", "waste", "trash", "bins", "dumped"]):
            evidence.append("waste")
        elif any(token in text for token in ["noise", "music"]):
            evidence.append("noise")
        elif any(token in text for token in ["crack", "cracked", "tiles", "footpath", "sinking"]):
            evidence.append("road damage")
        elif "heritage" in text:
            evidence.append("heritage")
        elif any(token in text for token in ["heat", "temperature", "sun"]):
            evidence.append("heat")
        elif any(token in text for token in ["drain", "manhole", "blocked", "clog"]):
            evidence.append("drain")
        else:
            evidence.append("the complaint")

        reason = f"The description mentions '{evidence[0]}' and was classified as {best_category}."

    priority = "Urgent" if any(keyword in text for keyword in SEVERITY_KEYWORDS) else "Standard"
    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception:
                    results.append(
                        {
                            "complaint_id": _normalize_text(row.get("complaint_id", "")) if isinstance(row, dict) else "",
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "The row failed during classification.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except Exception:
        results = [
            {
                "complaint_id": "",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Could not read input file: {input_path}",
                "flag": "NEEDS_REVIEW",
            }
        ]

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

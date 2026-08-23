"""
UC-0A — Complaint Classifier
Rule-based classifier using keyword detection.
See agents.md for enforcement rules and skills.md for error handling.
"""

import argparse
import csv
import re
from typing import Dict, List, Tuple

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Pothole":         ["pothole", "crater"],
    "Flooding":        ["flooded", "flood", "waterlog"],
    "Streetlight":     ["streetlight", "street light", "lights out", "lamp", "lighting", "sparking"],
    "Waste":           ["garbage", "waste", "trash", "litter", "dumping", "dead animal", "overflowing bin"],
    "Noise":           ["noise", "loud music", "honking", "noisy", "music past midnight"],
    "Road Damage":     ["road damage", "road surface", "manhole cover", "footpath", "road cracked", "cracked road", "sinking", "road broken", "pavement"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard":     ["heat", "hot"],
    "Drain Blockage":  ["drain blocked", "sewer blocked", "blocked drain"],
}


def _has_urgent_keywords(description: str) -> bool:
    lower = description.lower()
    return any(kw in lower for kw in URGENT_KEYWORDS)


def _get_category_scores(description: str) -> Dict[str, int]:
    lower = description.lower()
    scores: Dict[str, int] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in lower)
        if count > 0:
            scores[cat] = count
    return scores


def _classify(description: str) -> Tuple[str, str]:
    """Returns (category, flag) — flag is 'NEEDS_REVIEW' or empty string."""
    scores = _get_category_scores(description)

    if not scores:
        return "Other", "NEEDS_REVIEW"

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    top_cat, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    # Tied scores across distinct categories → genuinely ambiguous
    if top_score == second_score:
        return "Other", "NEEDS_REVIEW"

    return top_cat, ""


def _make_reason(category: str, description: str, flag: str) -> str:
    words = re.findall(r"[A-Za-z]{3,}", description)

    if flag == "NEEDS_REVIEW":
        if len(words) >= 2:
            return (
                f"Description is ambiguous: '{words[0]}' and '{words[1]}' "
                f"could indicate multiple categories."
            )
        return "Description is ambiguous and does not clearly match a single category."

    lower = description.lower()
    cited: List[str] = []
    for kw in CATEGORY_KEYWORDS.get(category, []):
        idx = lower.find(kw)
        if idx != -1:
            cited.append(description[idx: idx + len(kw)])
        if len(cited) >= 2:
            break

    if len(cited) < 2:
        for w in words:
            w_clean = w.strip(",.!?;:")
            if w_clean.lower() not in tuple(c.lower() for c in cited):
                cited.append(w_clean)
            if len(cited) >= 2:
                break

    if len(cited) >= 2:
        return f"Classified as {category} because description mentions '{cited[0]}' and '{cited[1]}'."
    if len(cited) == 1:
        return f"Classified as {category} because description mentions '{cited[0]}'."
    return f"Classified as {category} based on the description."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description was empty or unintelligible",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = _classify(description)
    priority = "Urgent" if _has_urgent_keywords(description) else "Standard"
    reason = _make_reason(category, description, flag)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV.

    Raises ValueError if 'description' column is missing.
    On per-row failure, writes fallback values and continues.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "description" not in reader.fieldnames:
            raise ValueError("Input CSV is missing the required 'description' column")

        results: List[dict] = []
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "Classification error",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

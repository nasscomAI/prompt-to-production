"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from typing import Dict, List, Tuple

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    allowed_categories = [
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
    allowed_priorities = ["Urgent", "Standard", "Low"]

    description = (row.get("description") or "").strip()
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": 'Missing description ("description" field empty).',
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # Enforcement: urgency keyword match must trigger Urgent.
    severity_keywords = [
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
    priority = "Urgent" if any(k in text for k in severity_keywords) else "Standard"

    # Category detection via lightweight keyword rules (exact output strings only).
    category_rules: List[Tuple[str, List[str]]] = [
        ("Pothole", ["pothole"]),
        ("Flooding", ["flood", "flooding", "waterlogged", "water logging", "inundat"]),
        ("Streetlight", ["streetlight", "street light", "unlit", "no light", "lights out", "lamp post", "lamp"]),
        ("Waste", ["waste", "garbage", "trash", "overflowing", "bins", "bin", "litter", "not cleared", "dump"]),
        ("Noise", ["noise", "noisy", "loud", "music", "dj", "horn", "audible"]),
        ("Drain Blockage", ["drain", "drainage", "sewer", "gutter", "blocked", "blockage", "choked", "clog"]),
        ("Heritage Damage", ["heritage", "ancient", "step well", "stepwell", "old city", "monument", "protected"]),
        ("Heat Hazard", ["heat", "heatwave", "temperature", "°c", "c.", "melting", "unbearable", "burn", "burns", "full sun", "unsafe"]),
        ("Road Damage", ["road", "surface", "tarmac", "subsidence", "sink", "crack", "bubbling", "paving", "lane closure", "divider", "dividers"]),
    ]

    matched: List[str] = []
    for cat, patterns in category_rules:
        if any(p in text for p in patterns):
            matched.append(cat)

    # Remove duplicates while preserving order.
    seen = set()
    matched = [m for m in matched if not (m in seen or seen.add(m))]

    flag = ""
    if not matched:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category = matched[0]
    else:
        # Prefer the more specific categories when heat/heritage overlaps with generic road damage.
        ranked = [c for c in matched if c in ("Heat Hazard", "Heritage Damage")] + [
            c for c in matched if c not in ("Heat Hazard", "Heritage Damage", "Road Damage")
        ]
        ranked += [c for c in matched if c == "Road Damage"]

        # If still effectively ambiguous, mark for review.
        category = ranked[0] if ranked else "Other"
        flag = "NEEDS_REVIEW"

    if category not in allowed_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in allowed_priorities:
        priority = "Standard"
        flag = "NEEDS_REVIEW"

    # One sentence, grounded: quote a short snippet from the description.
    snippet = re.sub(r"\s+", " ", description)
    snippet = snippet[:140] + ("…" if len(snippet) > 140 else "")
    reason = f'Classified as {category} because description says "{snippet}".'

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        input_fieldnames = reader.fieldnames or []

        output_fieldnames = list(input_fieldnames)
        for col in ["category", "priority", "reason", "flag"]:
            if col not in output_fieldnames:
                output_fieldnames.append(col)

        rows: List[Dict[str, str]] = []
        for row in reader:
            try:
                classification = classify_complaint(row)
                out_row = dict(row)
                out_row["category"] = classification.get("category", "Other")
                out_row["priority"] = classification.get("priority", "Standard")
                out_row["reason"] = classification.get("reason", 'Classified as Other because description could not be parsed.')
                out_row["flag"] = classification.get("flag", "NEEDS_REVIEW")
                rows.append(out_row)
            except Exception as e:
                desc = (row.get("description") or "").strip()
                snippet = re.sub(r"\s+", " ", desc)[:120]
                rows.append(
                    {
                        **row,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f'Row could not be classified due to error "{type(e).__name__}" on description "{snippet}".',
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

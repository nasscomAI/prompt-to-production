import argparse
import csv
import re


URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "crater", "dip in road"]),
    ("Flooding", ["flood", "flooded", "waterlog", "water logging", "water standing", "inundat"]),
    ("Streetlight", ["streetlight", "light out", "lights out", "flickering", "lamp post", "lighting", "street light"]),
    ("Waste", ["garbage", "waste", "trash", "refuse", "dumping", "litter", "debris", "dead animal", "bin overflow"]),
    ("Noise", ["noise", "noisy", "loud music", "honking", "loudspeaker"]),
    ("Road Damage", ["road damage", "cracked", "sinking", "broken road", "road surface", "manhole cover", "footpath", "pavement"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatwave", "temperature"]),
    ("Drain Blockage", ["drain", "drainage", "blocked drain", "sewer"]),
]


def _find_reason(description: str, category: str, matched_keywords: list[str]) -> str:
    desc_lower = description.lower()
    for kw in matched_keywords:
        idx = desc_lower.find(kw.lower())
        if idx != -1:
            start = max(0, idx - 20)
            end = min(len(description), idx + len(kw) + 40)
            snippet = description[start:end].strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(description):
                snippet = snippet + "..."
            return f"Description contains '{kw}' in: \"{snippet}\""
    return f"Classified as {category} based on description keywords"


def _get_urgency_keyword(description: str) -> str | None:
    desc_lower = description.lower()
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            return kw
    return None


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description",
            "flag": "NEEDS_REVIEW",
        }

    matched_category = None
    matched_keywords = []

    for cat, keywords in CATEGORY_RULES:
        desc_lower = description.lower()
        for kw in keywords:
            if kw in desc_lower:
                matched_category = cat
                matched_keywords.append(kw)
                break
        if matched_category:
            break

    urgency_kw = _get_urgency_keyword(description)

    if matched_category is None:
        matched_category = "Other"

    if matched_category == "Other":
        priority = "Standard"
        flag = "NEEDS_REVIEW"
    elif urgency_kw:
        priority = "Urgent"
        flag = ""
    else:
        priority = "Standard"
        flag = ""

    reason = _find_reason(description, matched_category, matched_keywords)

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows_in = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows_in.append(row)

    fieldnames = list(rows_in[0].keys()) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        failed = 0
        for row in rows_in:
            total += 1
            try:
                result = classify_complaint(row)
                row["category"] = result["category"]
                row["priority"] = result["priority"]
                row["reason"] = result["reason"]
                row["flag"] = result["flag"]
            except Exception:
                failed += 1
                row["category"] = "Other"
                row["priority"] = "Low"
                row["reason"] = "Classification error"
                row["flag"] = "NEEDS_REVIEW"
            writer.writerow(row)

    print(f"Processed {total} rows, {failed} failed. Written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import logging

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole",         ["pothole"]),
    ("Heritage Damage", ["heritage", "historic", "historical", "monument"]),
    ("Heat Hazard",     ["heat wave", "heatwave", "heatstroke", "sunstroke", "extreme heat"]),
    ("Streetlight",     ["streetlight", "lights out", "light out", "lamp post", "flickering", "sparking", "unlit"]),
    ("Flooding",        ["flooded", "flooding", "flood", "waterlogging", "submerged", "water logged"]),
    ("Drain Blockage",  ["drain", "drainage", "sewer", "manhole", "clogged", "blocked drain"]),
    ("Waste",           ["garbage", "waste", "trash", "rubbish", "overflowing bin", "dead animal", "dumping", "litter", "stench"]),
    ("Noise",           ["noise", "music", "loud", "honking", "party", "amplifier", "band", "drilling"]),
    ("Road Damage",     ["road damage", "road surface", "cracked", "sinking", "collapsed", "subsided", "footpath", "pavement"]),
]

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def _find_original_substrings(text: str, keywords: list[str]) -> list[str]:
    text_lower = text.lower()
    found = []
    for kw in keywords:
        idx = text_lower.find(kw)
        if idx != -1:
            found.append(text[idx:idx + len(kw)])
    return found


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = "Other"
    matched_cat_kws = []
    for cat, kws in CATEGORY_RULES:
        found = [kw for kw in kws if kw in desc_lower]
        if found:
            category = cat
            matched_cat_kws = _find_original_substrings(description, found)
            break
    if category == "Heritage Damage":
        for override_cat in ("Waste", "Noise"):
            oc_kws = [kw for c, kws in CATEGORY_RULES if c == override_cat for kw in kws]
            if any(kw in desc_lower for kw in oc_kws):
                category = override_cat
                oc_found = [kw for kw in oc_kws if kw in desc_lower]
                matched_cat_kws = _find_original_substrings(description, oc_found)
                break

    matched_sev_kws = _find_original_substrings(
        description, [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    )
    priority = "Urgent" if matched_sev_kws else "Standard"

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    if category == "Other":
        words = description.split()
        cited = ", ".join(f"'{w}'" for w in words[:5])
        extra = " ..." if len(words) > 5 else ""
        reason = f"Description mentions {cited}{extra} but no category keyword matched; assigned Other for review."
        if matched_sev_kws:
            sev_str = ", ".join(f"'{kw}'" for kw in matched_sev_kws)
            reason = f"Description mentions {cited}{extra} but no category keyword matched; assigned Other for review. Contains severity keyword(s) {sev_str} requiring Urgent priority."
    else:
        cat_kw_str = ", ".join(f"'{kw}'" for kw in matched_cat_kws)
        if matched_sev_kws:
            sev_str = ", ".join(f"'{kw}'" for kw in matched_sev_kws)
            reason = f"Description mentions {cat_kw_str} indicating {category} and contains severity keyword(s) {sev_str} requiring Urgent priority."
        else:
            reason = f"Description mentions {cat_kw_str} indicating {category}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                logging.warning("Row %d (ID: %s) failed: %s", i, row.get("complaint_id", "?"), e)

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

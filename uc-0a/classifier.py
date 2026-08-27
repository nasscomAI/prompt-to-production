"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    # Rule-based classifier implementing agents.md enforcement with regex matching.
    text = (row.get("description") or "").strip()
    cid = row.get("complaint_id") or row.get("id") or ""
    original = text
    lowered = text.lower()

    categories = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flood", "flooding", "waterlogged", "water logged", "water logging", "waterlogged"],
        "Streetlight": ["streetlight", "street light", "broken lamp", "lamp", "light out", "light not working"],
        "Waste": ["garbage", "waste", "trash", "bin", "rubbish"],
        "Noise": ["noise", "loud", "loud music", "music"],
        "Road Damage": ["road damage", "crack", "cracked", "broken road", "sinkhole"],
        "Heritage Damage": ["heritage", "monument", "statue", "graffiti"],
        "Heat Hazard": ["heatwave", "heat wave", "heat", "very hot"],
        "Drain Blockage": ["blocked drain", "blocked", "clog", "clogged", "overflowing drain", "drainage", "drain"]
    }

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    # Priority determination (Urgent if any severity keyword present)
    priority = "Standard"
    severity_matched = None
    for sk in severity_keywords:
        pattern = r"\b" + re.escape(sk) + r"\b"
        m = re.search(pattern, original, flags=re.IGNORECASE)
        if m:
            priority = "Urgent"
            severity_matched = m.group(0)
            break

    # Category matching with regex word boundaries; capture the actual matched text for citation
    matched = []  # list of (category, matched_text)
    for cat, kws in categories.items():
        for kw in kws:
            pattern = r"\b" + re.escape(kw) + r"\b"
            m = re.search(pattern, original, flags=re.IGNORECASE)
            if m:
                matched.append((cat, m.group(0)))
                break

    flag = ""
    if not original:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Empty description; cannot determine category."
    else:
        cats = [c for c, _ in matched]
        unique_cats = list(dict.fromkeys(cats))
        if len(unique_cats) == 1:
            category = unique_cats[0]
            cited = matched[0][1]
            reason = f"Mentions '{cited}' in the description, indicating {category}."
        elif len(unique_cats) > 1:
            category = "Other"
            flag = "NEEDS_REVIEW"
            cited_list = ", ".join(f"'{m}'" for _, m in matched)
            reason = f"Mentions multiple keywords ({cited_list}) making category ambiguous."
        else:
            # No category matched
            category = "Other"
            flag = "NEEDS_REVIEW"
            if severity_matched:
                reason = f"No category keyword matched but mentions severity word '{severity_matched}'."
            else:
                # Cite a short excerpt from the original description
                excerpt = " ".join(original.split()[:6])
                reason = f"No category keyword matched; description excerpt: '{excerpt}'."

    if not reason.endswith("."):
        reason = reason + "."

    return {
        "complaint_id": cid,
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
    # Read input CSV, classify rows, and write output CSV robustly.
    rows_out = []
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader, start=1):
            try:
                out = classify_complaint(row)
            except Exception:
                out = {
                    "complaint_id": row.get("complaint_id") or row.get("id") or f"row_{i}",
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error during classification; marked for review.",
                    "flag": "NEEDS_REVIEW",
                }
            rows_out.append(out)

    # Write output CSV with required columns
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfh:
        writer = csv.DictWriter(outfh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows_out:
            writer.writerow(r)
    # Build and return a small report per skills.md
    rows_processed = len(rows_out)
    rows_flagged = sum(1 for r in rows_out if (r.get("flag") or "") == "NEEDS_REVIEW")
    return {"rows_processed": rows_processed, "rows_flagged": rows_flagged}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    report = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
    print(f"Report: processed={report.get('rows_processed')} flagged={report.get('rows_flagged')}")

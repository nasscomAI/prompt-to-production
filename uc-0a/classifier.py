"""
UC-0A - Complaint Classifier
Built using RICE agents.md enforcement
"""
import argparse
import csv
import re
import os

ALLOWED_CATEGORIES = [
    "Pothole", "Streetlight_Out", "Flooding", "Garbage_Overflow",
    "Water_Leak", "Sewage_Backup", "Traffic_Signal_Fault",
    "Park_Maintenance", "Other"
]

URGENT_KEYWORDS = ["injury", "injured", "child", "school", "hospital", "accident", "sewage in home", "no water", "electric shock", "danger", "unsafe", "blocked road", "bleeding", "emergency"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "road hole", "crack in road", "pavement hole", "bump"],
    "Streetlight_Out": ["streetlight", "street light", "lamp post", "light not working", "dark street"],
    "Flooding": ["flooding", "flooded", "water logging", "waterlogged", "standing water", "drain overflow"],
    "Garbage_Overflow": ["garbage", "trash", "waste overflow", "bin full", "litter", "dump"],
    "Water_Leak": ["water leak", "pipe leak", "leaking pipe", "water supply leak", "burst pipe"],
    "Sewage_Backup": ["sewage", "sewer", "manhole", "bad smell", "sewage backup", "drain smell"],
    "Traffic_Signal_Fault": ["traffic signal", "traffic light", "signal not working", "red light stuck"],
    "Park_Maintenance": ["park", "playground", "bench broken", "grass", "garden maintenance"]
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority_flag, reason, confidence
    """
    complaint_id = str(row.get("complaint_id", "") or row.get("id", "") or "unknown").strip()
    # support multiple possible text columns
    text_raw = row.get("description", "") or row.get("complaint_text", "") or row.get("text", "") or ""

    # RICE: Flag nulls
    if text_raw is None or str(text_raw).strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority_flag": "Low",
            "reason": "empty/null input flagged",
            "confidence": "Low"
        }

    text = str(text_raw).strip()
    text_lower = text.lower()

    # Find category
    best_category = "Other"
    matched_words = []
    max_hits = 0
    possible_cats = []

    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = 0
        found = []
        for kw in keywords:
            if kw in text_lower:
                hits += 1
                found.append(kw)
        if hits > 0:
            possible_cats.append(cat)
        if hits > max_hits:
            max_hits = hits
            best_category = cat
            matched_words = found

    # Ambiguity check
    if len(possible_cats) > 1 and max_hits == 1:
        confidence = "Low"
        reason_words = ", ".join(matched_words[:2]) if matched_words else text.split()[:3]
        reason = f"ambiguous between {', '.join(possible_cats[:2])}, contains \"{reason_words}\""
    elif best_category == "Other":
        confidence = "Low" if len(text.split()) < 4 else "Medium"
        # quote first 2-4 words
        snippet = " ".join(text.split()[:4])
        reason = f"no clear keyword match, contains \"{snippet}\""
    else:
        confidence = "High" if max_hits >= 2 else "Medium"
        quote = matched_words[0] if matched_words else " ".join(text.split()[:3])
        reason = f"contains \"{quote}\""

    # Priority
    priority = "Low"
    urgent_found = [k for k in URGENT_KEYWORDS if k in text_lower]
    if urgent_found:
        priority = "Urgent"
        reason += f" and urgent keyword \"{urgent_found[0]}\""
    elif any(w in text_lower for w in ["road", "garbage", "sewage", "water", "light", "traffic"]):
        priority = "Routine"

    # Low confidence override for vague
    if len(text.split()) <= 2:
        confidence = "Low"
        priority = "Routine" if priority == "Low" else priority

    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority_flag": priority,
        "reason": reason,
        "confidence": confidence
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV
    Must: flag nulls, not crash on bad rows, produce output for all rows
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    rows = []
    try:
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    classified = classify_complaint(r)
                    rows.append(classified)
                except Exception as e:
                    # Never crash on bad row
                    cid = r.get("complaint_id", "unknown")
                    rows.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority_flag": "Low",
                        "reason": f"bad row flagged: {str(e)[:50]}",
                        "confidence": "Low"
                    })
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        return

    # Write output
    with open(output_path, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=["complaint_id", "category", "priority_flag", "reason", "confidence"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Wrote {len(rows)} rows to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

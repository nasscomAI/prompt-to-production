"""
UC-0A — Complaint Classifier
Classifies civic complaints: category + priority + reason + flag.
Rule-based enforcement per agents.md — no external API required.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
    python classifier.py --input ../data/city-test-files/test_pune.csv   # stdout
"""
import argparse
import csv
import sys
from collections import Counter

# ── Allowed taxonomy (exact strings, agents.md enforcement rule 1) ─────────────
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords → Urgent (agents.md enforcement rule 2)
URGENT_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "fallen", "collapse", "collapsed",
    "risk", "danger", "dangerous", "accident", "emergency", "serious",
]

# Category keyword map — longest/most-specific match first
CATEGORY_KEYWORDS = {
    "Drain Blockage":  ["drain blocked", "blocked drain", "drain blockage",
                        "drainage", "manhole", "sewer", "waterway"],
    "Pothole":         ["pothole", "pot hole", "crater", "tyre damage"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlogged",
                        "knee-deep", "standing water", "inundated"],
    "Streetlight":     ["streetlight", "street light", "light out", "lights out",
                        "sparking", "flickering", "lamp post", "no lighting"],
    "Waste":           ["garbage", "waste", "trash", "rubbish", "overflowing bin",
                        "bins", "dumped", "dump", "dead animal", "animal not removed",
                        "bulk waste", "litter"],
    "Noise":           ["noise", "loud music", "playing music", "midnight",
                        "loudspeaker", "wedding", "party"],
    "Road Damage":     ["road surface", "cracked", "sinking", "footpath",
                        "tiles broken", "tiles upturned", "pavement broken",
                        "road damage", "road crack"],
    "Heritage Damage": ["heritage", "historic", "monument", "heritage street",
                        "old city", "heritage site"],
    "Heat Hazard":     ["heat", "heatwave", "extreme temperature", "heat hazard"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description  = row.get("description", "")
    desc_lower   = description.lower()

    # ── Category detection ─────────────────────────────────────────────────────
    matched: list[tuple[str, str]] = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched.append((cat, kw))
                break

    if not matched:
        category   = "Other"
        reason_kw  = "no keywords matched any known category"
        flag       = "NEEDS_REVIEW"
    elif len(matched) == 1:
        category   = matched[0][0]
        reason_kw  = matched[0][1]
        flag       = ""
    else:
        # Multiple categories matched — pick first, flag for review
        category   = matched[0][0]
        reason_kw  = ", ".join(f"{c}='{k}'" for c, k in matched)
        flag       = "NEEDS_REVIEW"

    # ── Priority detection (agents.md enforcement rule 2) ─────────────────────
    urgent_trigger = next(
        (kw for kw in URGENT_KEYWORDS if kw in desc_lower), None
    )

    if urgent_trigger:
        priority = "Urgent"
        reason   = (
            f"Classified as {category} based on '{matched[0][1] if matched else 'Other'}'; "
            f"priority Urgent triggered by keyword '{urgent_trigger}'"
        )
    else:
        priority = "Standard"
        reason   = (
            f"Classified as {category} based on '{reason_kw}' in description"
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str = None) -> list:
    """
    Reads input CSV, classifies every row, writes output CSV.
    Returns list of result dicts.
    """
    results = []
    errors  = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    if not rows:
        print("[ERROR] Input file is empty or has no data rows.")
        sys.exit(1)

    for row in rows:
        try:
            results.append(classify_complaint(row))
        except Exception as e:
            errors.append({"complaint_id": row.get("complaint_id"), "error": str(e)})

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    if output_path:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"[OK] {len(results)} rows written to: {output_path}")
        if errors:
            print(f"[WARN] {len(errors)} rows failed: {errors}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return results


def print_summary(results: list):
    cats    = Counter(r["category"] for r in results)
    prios   = Counter(r["priority"] for r in results)
    reviews = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")

    print("\n" + "═" * 70)
    print("CLASSIFICATION SUMMARY")
    print("═" * 70)
    print(f"Total complaints : {len(results)}")
    print(f"NEEDS_REVIEW     : {reviews}")
    print()
    print("By Category:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20} {count}")
    print()
    print("By Priority:")
    for prio in ["Urgent", "Standard", "Low"]:
        print(f"  {prio:<12} {prios.get(prio, 0)}")
    print()
    urgent = [r for r in results if r["priority"] == "Urgent"]
    if urgent:
        print("URGENT Complaints:")
        for r in urgent:
            print(f"  [{r['complaint_id']}] {r['category']}")
            print(f"    → {r['reason']}")
    print("═" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True,  help="Path to test_[city].csv")
    parser.add_argument("--output", required=False, help="Path to write results CSV (optional)")
    args = parser.parse_args()

    results = batch_classify(args.input, args.output)
    print_summary(results)

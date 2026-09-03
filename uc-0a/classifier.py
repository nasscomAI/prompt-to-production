"""
UC-0A classifier.py — Complaint classifier that follows the schema
defined in README.md and the enforcement rules in agents.md.

Usage:
    python classifier.py \
        --input ../data/city-test-files/test_pune.csv \
        --output results_tirupati.csv
"""
import argparse
import csv
import re
import sys
from typing import Dict, List

CATEGORIES: List[str] = [
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

PRIORITIES: List[str] = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

REQUIRED_INPUT_COLS = [
    "complaint_id", "date_raised", "city", "ward", "location",
    "description", "reported_by", "days_open",
]


def fail(msg: str) -> "None":
    sys.stderr.write(f"UC-0A: {msg}\n")
    sys.exit(1)


# --- skill: classify_complaint ---------------------------------------------

CATEGORY_PATTERNS: List[tuple] = [
    ("Pothole",         [r"\bpothole\b", r"tyre damage", r"vehicle"]),
    ("Flooding",        [r"\bflood", r"flooded", r"knee-deep", r"in water"]),
    ("Streetlight",     [r"streetlight", r"street light", r"lights out", r"sparking", r"flickering"]),
    ("Drain Blockage",  [r"drain block", r"drainage", r"sewage", r"overflow"]),
    ("Waste",           [r"garbage", r"waste", r"dumped", r"dead animal", r"smell"]),
    ("Noise",           [r"music", r"noise", r"loudspeaker", r"loud"]),
    ("Heritage Damage", [r"heritage", r"old city", r"monument", r"historic"]),
    ("Heat Hazard",     [r"heat wave", r"heatstroke", r"dehydration"]),
    ("Road Damage",     [r"road surface", r"crack", r"sinking", r"footpath", r"tiles broken", r"manhole"]),
]


def _distinctive_quote(desc: str) -> str:
    """Pick a short, distinctive phrase from the description to quote."""
    toks = re.findall(r"[A-Za-z][A-Za-z\-]+", desc)
    for t in toks:
        if len(t) >= 5 and t.lower() not in {"near", "after", "before", "since", "during", "there", "their", "which", "where", "because"}:
            return t
    return toks[0] if toks else "complaint"


def classify_complaint(row: Dict[str, str]) -> Dict[str, str]:
    desc = (row.get("description") or "").strip()
    loc = (row.get("location") or "").strip()
    blob = f"{desc} {loc}".lower()

    if not desc:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    hits: Dict[str, List[str]] = {}
    for cat, patterns in CATEGORY_PATTERNS:
        matched = [p for p in patterns if re.search(p, blob, flags=re.IGNORECASE)]
        if matched:
            hits[cat] = matched

    if not hits:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(hits) == 1:
        category = next(iter(hits))
        flag = ""
    else:
        ranked = sorted(hits.items(), key=lambda kv: -len(kv[1]))
        if len(ranked[0][1]) >= 2 and len(ranked[0][1]) > len(ranked[1][1]):
            category = ranked[0][0]
            flag = ""
        else:
            category = ranked[0][0]
            flag = "NEEDS_REVIEW"

    severity_hit = next((kw for kw in SEVERITY_KEYWORDS if kw in blob), None)
    if severity_hit:
        priority = "Urgent"
    else:
        days_open_raw = row.get("days_open") or ""
        try:
            days_open = int(days_open_raw)
        except ValueError:
            days_open = 0
        if days_open >= 14:
            priority = "Standard"
        else:
            priority = "Standard" if "water" in blob or "flood" in blob else "Low"

    quote = _distinctive_quote(desc)
    if severity_hit:
        reason = f"Description contains severity keyword '{severity_hit}' (quoted from row: \"{quote}\"); priority set to Urgent."
    else:
        reason = f"Description references '{quote}' which maps to category {category}."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# --- skill: batch_classify --------------------------------------------------

def batch_classify(in_path: str, out_path: str) -> None:
    try:
        with open(in_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                fail(f"input CSV has no header: {in_path}")
            missing = [c for c in REQUIRED_INPUT_COLS if c not in reader.fieldnames]
            if missing:
                fail(f"input CSV missing required columns: {missing}")
            rows = list(reader)
    except FileNotFoundError:
        fail(f"input file not found: {in_path}")
    except OSError as e:
        fail(f"cannot read input file {in_path}: {e}")

    if not rows:
        fail("input CSV has no data rows")

    out_rows: List[Dict[str, str]] = []
    for r in rows:
        cls = classify_complaint(r)
        merged = {k: r.get(k, "") for k in r.keys()}
        merged["category"] = cls["category"]
        merged["priority"] = cls["priority"]
        merged["reason"] = cls["reason"]
        merged["flag"] = cls["flag"]
        out_rows.append(merged)

    for r in out_rows:
        if r["category"] not in CATEGORIES:
            fail(f"internal error: category '{r['category']}' is outside the allowed enum")
        if r["priority"] not in PRIORITIES:
            fail(f"internal error: priority '{r['priority']}' is outside the allowed enum")
        blob = (r.get("description", "") + " " + r.get("location", "")).lower()
        if any(kw in blob for kw in SEVERITY_KEYWORDS) and r["priority"] != "Urgent":
            fail(
                f"severity keyword in description of {r.get('complaint_id')} but "
                f"priority is {r['priority']} (must be Urgent)"
            )

    try:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = list(rows[0].keys()) + ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in out_rows:
                writer.writerow(r)
    except OSError as e:
        fail(f"cannot write output file {out_path}: {e}")


# --- entrypoint -------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0A complaint classifier")
    parser.add_argument("--input", required=True, help="path to complaints CSV")
    parser.add_argument("--output", required=True, help="path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)


if __name__ == "__main__":
    main()

"""Validate results CSV against every agents.md enforcement rule."""
import csv
import re
import sys

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}
ALLOWED_PRIORITIES = {"Urgent", "Standard", "Low"}
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
}
HEDGING = [
    "possibly", "might be", "could indicate", "appears to be",
    "generally", "typically", "it seems",
]
OUTPUT_COLS = ["category", "priority", "reason", "flag"]

results_file = sys.argv[1] if len(sys.argv) > 1 else "results_pune.csv"

with open(results_file, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

errors = []
for r in rows:
    cid = r.get("complaint_id", "?")

    # Rule 1: category must be in allowed set
    cat = r.get("category", "")
    if cat not in ALLOWED_CATEGORIES:
        errors.append(cid + ": BAD CATEGORY [" + cat + "]")

    # Rule 2: priority must be in allowed set
    pri = r.get("priority", "")
    if pri not in ALLOWED_PRIORITIES:
        errors.append(cid + ": BAD PRIORITY [" + pri + "]")

    # Rule 3: severity keyword must force Urgent
    desc = r.get("description", "").lower()
    has_sev = any(re.search(r"\b" + kw + r"\b", desc) for kw in SEVERITY_KEYWORDS)
    if has_sev and pri != "Urgent":
        errors.append(cid + ": SEVERITY MISSED — got " + pri + " instead of Urgent")

    # Rule 4: reason must not be empty
    reason = r.get("reason", "")
    if not reason.strip():
        errors.append(cid + ": EMPTY REASON")

    # Rule 5: no hedging in reason
    for h in HEDGING:
        if h in reason.lower():
            errors.append(cid + ": HEDGING in reason [" + h + "]")

    # Rule 6: flag must be NEEDS_REVIEW or blank
    flag = r.get("flag", "")
    if flag not in ("NEEDS_REVIEW", ""):
        errors.append(cid + ": BAD FLAG [" + flag + "]")

    # Rule 7: all four output fields must be present
    for col in OUTPUT_COLS:
        if col not in r:
            errors.append(cid + ": MISSING FIELD [" + col + "]")

print("Rows validated:", len(rows))
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
else:
    print("ALL ENFORCEMENT CHECKS PASSED —", len(rows), "/", len(rows), "rows valid")

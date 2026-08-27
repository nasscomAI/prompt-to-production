"""
Validates classifier output against UC-0A enforcement rules.
Run from repo root: python uc-0a/validate_results.py
"""
import csv
import glob

VALID_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}
VALID_PRIORITIES = {"Urgent", "Standard", "Low"}
URGENT_KEYWORDS  = ["injury", "child", "school", "hospital", "ambulance",
                    "fire", "hazard", "fell", "collapse"]
VALID_FLAGS      = {"NEEDS_REVIEW", ""}

errors   = []
warnings = []
total    = 0

for path in sorted(glob.glob("uc-0a/results_*.csv")):
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            total += 1
            cid  = r["complaint_id"]
            desc = r["description"].lower()
            cat  = r["category"]
            pri  = r["priority"]
            flag = r["flag"]
            rsn  = r["reason"]

            # Rule 1: exact category
            if cat not in VALID_CATEGORIES:
                errors.append(f"[{path}] {cid}: invalid category '{cat}'")

            # Rule 2: exact priority
            if pri not in VALID_PRIORITIES:
                errors.append(f"[{path}] {cid}: invalid priority '{pri}'")

            # Rule 3: must be Urgent if urgent keyword present
            has_urgent = any(kw in desc for kw in URGENT_KEYWORDS)
            if has_urgent and pri != "Urgent":
                errors.append(f"[{path}] {cid}: URGENT keyword in desc but priority='{pri}'")

            # Rule 4: reason must not be empty
            if not rsn.strip():
                errors.append(f"[{path}] {cid}: reason field is empty")

            # Rule 5: valid flag values
            if flag not in VALID_FLAGS:
                errors.append(f"[{path}] {cid}: invalid flag '{flag}'")

            # Warning: Other without NEEDS_REVIEW
            if cat == "Other" and flag != "NEEDS_REVIEW":
                warnings.append(f"[{path}] {cid}: category=Other but flag not set to NEEDS_REVIEW")

print(f"\n{'='*60}")
print(f"  UC-0A Validation Report — {total} rows across {len(glob.glob('uc-0a/results_*.csv'))} cities")
print(f"{'='*60}")
if errors:
    print(f"\n  [FAIL] {len(errors)} ERRORS:")
    for e in errors:
        print(f"     {e}")
else:
    print("\n  [PASS] All enforcement rules PASSED")

if warnings:
    print(f"\n  [WARN] {len(warnings)} WARNINGS:")
    for w in warnings:
        print(f"     {w}")
else:
    print("  [PASS] No warnings")
print()

"""Test classifier against agents.md enforcement rules."""
import csv
import sys

ALLOWED_CATEGORIES = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def load_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def test_enforcement_rules(results_path):
    rows = load_csv(results_path)
    errors = []
    warnings = []

    for row in rows:
        cid = row["complaint_id"]
        cat = row["category"]
        pri = row["priority"]
        reason = row["reason"]
        flag = row["flag"]

        # Rule 1: Category must be exactly one of allowed list
        if cat not in ALLOWED_CATEGORIES:
            errors.append(f"{cid}: Category '{cat}' not in allowed list")

        # Rule 2: Priority must be one of allowed values
        if pri not in ALLOWED_PRIORITIES:
            errors.append(f"{cid}: Priority '{pri}' not in allowed list")

        # Rule 3: Reason must be one sentence citing specific words
        if not reason or len(reason.strip()) < 10:
            errors.append(f"{cid}: Reason too short or missing: '{reason}'")

        # Rule 4: Flag must be NEEDS_REVIEW or blank
        if flag and flag != "NEEDS_REVIEW":
            errors.append(f"{cid}: Flag '{flag}' not allowed")

    return errors, warnings, len(rows)

def test_severity_keywords(input_path, results_path):
    """Check that severity keywords trigger Urgent priority."""
    inputs = load_csv(input_path)
    results = load_csv(results_path)
    errors = []

    input_map = {r["complaint_id"]: r for r in inputs}
    result_map = {r["complaint_id"]: r for r in results}

    for cid in input_map:
        desc = input_map[cid].get("description", "").lower()
        priority = result_map.get(cid, {}).get("priority", "")

        has_severity = any(kw in desc for kw in SEVERITY_KEYWORDS)
        if has_severity and priority != "Urgent":
            errors.append(f"{cid}: Has severity keyword but priority is '{priority}' (should be Urgent)")

    return errors

if __name__ == "__main__":
    cities = ["pune", "ahmedabad", "hyderabad", "kolkata"]
    total_errors = 0
    total_rows = 0

    for city in cities:
        input_path = f"../data/city-test-files/test_{city}.csv"
        results_path = f"results_{city}.csv"

        print(f"\n{'='*60}")
        print(f"Testing: {city.upper()}")
        print(f"{'='*60}")

        try:
            rule_errors, warnings, count = test_enforcement_rules(results_path)
            severity_errors = test_severity_keywords(input_path, results_path)

            all_errors = rule_errors + severity_errors
            total_errors += len(all_errors)
            total_rows += count

            if all_errors:
                for e in all_errors:
                    print(f"  FAIL: {e}")
            else:
                print(f"  PASS: {count} rows classified correctly")

        except FileNotFoundError:
            print(f"  SKIP: Results file not found")

    print(f"\n{'='*60}")
    print(f"SUMMARY: {total_rows} rows tested, {total_errors} errors")
    print(f"{'='*60}")
    sys.exit(1 if total_errors > 0 else 0)

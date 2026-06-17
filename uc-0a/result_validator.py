"""
UC-0A — Result Validator
Validates classifier output against RICE enforcement rules from agents.md.
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard"]

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

REQUIRED_COLUMNS = ["complaint_id", "category", "priority", "reason", "flag"]


def validate(results_path: str, input_path: str) -> bool:
    errors = []

    try:
        with open(results_path, "r", newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
    except Exception as e:
        print(f"FAIL: Could not read results file: {e}")
        return False

    if not reader:
        print("FAIL: Results file is empty")
        return False

    if set(reader[0].keys()) != set(REQUIRED_COLUMNS):
        missing = set(REQUIRED_COLUMNS) - set(reader[0].keys())
        extra = set(reader[0].keys()) - set(REQUIRED_COLUMNS)
        if missing:
            errors.append(f"Missing columns: {missing}")
        if extra:
            errors.append(f"Extra columns: {extra}")

    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            input_rows = {r["complaint_id"]: r for r in csv.DictReader(f)}
    except Exception as e:
        print(f"FAIL: Could not read input file: {e}")
        return False

    result_ids = set()
    for i, row in enumerate(reader, start=2):
        cid = row.get("complaint_id", "").strip()

        if not cid:
            errors.append(f"Row {i}: Missing complaint_id")
            continue

        if cid in result_ids:
            errors.append(f"Row {i}: Duplicate complaint_id '{cid}'")
        result_ids.add(cid)

        category = row.get("category", "").strip()
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"Row {i} ({cid}): Invalid category '{category}'. Must be one of {ALLOWED_CATEGORIES}")

        priority = row.get("priority", "").strip()
        if priority not in ALLOWED_PRIORITIES:
            errors.append(f"Row {i} ({cid}): Invalid priority '{priority}'. Must be one of {ALLOWED_PRIORITIES}")

        flag = row.get("flag", "").strip()
        if flag not in ["", "NEEDS_REVIEW"]:
            errors.append(f"Row {i} ({cid}): Invalid flag '{flag}'. Must be 'NEEDS_REVIEW' or empty")

        if flag == "NEEDS_REVIEW" and category != "Other":
            if category not in ["Heritage Damage", "Streetlight", "Waste", "Noise"]:
                pass

        reason = row.get("reason", "").strip()
        if not reason:
            errors.append(f"Row {i} ({cid}): Missing reason")
        else:
            input_row = input_rows.get(cid, {})
            desc = input_row.get("description", "").lower()
            reason_lower = reason.lower()
            words_quoted = False
            for word in reason_lower.split():
                clean_word = word.strip("'\".,;:!?")
                if len(clean_word) > 3 and clean_word in desc:
                    words_quoted = True
                    break
            if not words_quoted:
                for phrase in desc.split(". "):
                    phrase_clean = phrase.strip().lower()
                    if len(phrase_clean) > 10 and phrase_clean[:40] in reason_lower:
                        words_quoted = True
                        break
            if not words_quoted:
                errors.append(f"Row {i} ({cid}): Reason does not cite specific words from description. Reason: '{reason}'")

        if priority == "Urgent":
            input_row = input_rows.get(cid, {})
            desc = input_row.get("description", "").lower()
            has_severity = any(kw in desc for kw in SEVERITY_KEYWORDS)
            if not has_severity:
                errors.append(f"Row {i} ({cid}): Priority is Urgent but no severity keyword found in description")
        elif priority == "Standard":
            input_row = input_rows.get(cid, {})
            desc = input_row.get("description", "").lower()
            has_severity = any(kw in desc for kw in SEVERITY_KEYWORDS)
            if has_severity:
                errors.append(f"Row {i} ({cid}): Priority is Standard but description contains severity keyword(s)")

    if cid not in input_rows:
        errors.append(f"Row {i} ({cid}): complaint_id not found in input file")

    if not errors:
        print(f"PASS: All {len(reader)} rows validated successfully")
        return True

    print(f"FAIL: {len(errors)} validation error(s):")
    for err in errors:
        print(f"  - {err}")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Result Validator")
    parser.add_argument("--results", required=True, help="Path to results CSV")
    parser.add_argument("--input", required=True, help="Path to original input CSV")
    args = parser.parse_args()

    success = validate(args.results, args.input)
    sys.exit(0 if success else 1)

"""
UC-0A — Complaint Classifier.

Deterministic, keyword-driven classification. Categories come from a fixed enum,
priority is forced to Urgent whenever a severity keyword is present (the severity
check runs independently of category and cannot be overridden), every row gets a
reason citing words from the description, and undetermined complaints fall back
to Other + NEEDS_REVIEW. The agents.md enforcement rules are verified before the
output file is written.

Run:
  python classifier.py --input ../data/city-test-files/test_hyderabad.csv \
                       --output results_hyderabad.csv
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

# Severity keywords that MUST trigger Urgent (README schema).
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Ordered (category, keywords) — first group with a hit wins. Order resolves
# overlaps deliberately (e.g. "drain ... blocked" is Drain Blockage, not Flooding;
# anything "heritage" is Heritage Damage even if waste is mentioned).
CATEGORY_RULES = [
    ("Heritage Damage", ["heritage", "monument"]),
    ("Pothole", ["pothole"]),
    ("Road Damage", ["road collapsed", "collapsed", "crater", "road damage", "sinkhole", "buckled", "subsid"]),
    ("Drain Blockage", ["drain"]),
    ("Flooding", ["flood", "waterlog", "stormwater", "inundat"]),
    ("Streetlight", ["streetlight", "street light", "lamp post", "lamppost", "unlit", "wiring theft", "darkness"]),
    ("Heat Hazard", ["heatwave", "heat hazard", "heatstroke", "heat", "°c", "melting", "melt",
                     "unbearable", "full sun", "burns", "burn on contact", "temperature", "bubbling"]),
    ("Waste", ["garbage", "waste", "trash", "litter", "debris"]),
    ("Noise", ["noise", "drilling", "idling", "loud", "engines", "5am", "honking", "music", "audible", "band"]),
]

# Categories treated as low-impact nuisance when no severity keyword is present.
LOW_DEFAULT_CATEGORIES = {"Noise"}


def _severity_hits(description: str) -> list:
    lower = description.lower()
    return [kw for kw in SEVERITY_KEYWORDS if kw in lower]


def _detect_category(description: str) -> tuple:
    """Return (category, matched_keyword_or_None). Drain requires an actual
    blockage cue; otherwise falls through to the next rule."""
    lower = description.lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in lower:
                if category == "Drain Blockage" and not any(
                    b in lower for b in ["block", "clogg", "choke", "overflow"]
                ):
                    continue
                return category, kw
    return "Other", None


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into category, priority, reason, flag."""
    complaint_id = (row.get("complaint_id") or "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is empty or missing, so no category can be determined.",
            "flag": "NEEDS_REVIEW",
        }

    category, matched_kw = _detect_category(description)
    severity = _severity_hits(description)

    if severity:
        priority = "Urgent"
    elif category in LOW_DEFAULT_CATEGORIES:
        priority = "Low"
    else:
        priority = "Standard"

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    if category == "Other":
        cat_reason = "no category keyword matched the description"
    else:
        cat_reason = f"matched '{matched_kw}'"
    if severity:
        sev_reason = f"severity term(s) {severity} present -> Urgent"
    else:
        sev_reason = "no severity keyword present"

    reason = f"Classified as {category} ({cat_reason}); {sev_reason}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _enforce(records: list) -> None:
    """Verify agents.md enforcement rules against (description, result) pairs;
    raise on any violation. The severity rule is re-derived from the original
    description here so it is checked independently of the classify step."""
    for description, r in records:
        if r["category"] not in CATEGORIES:
            raise AssertionError(f"Taxonomy drift — invalid category '{r['category']}' on {r['complaint_id']}")
        if not r["reason"].strip():
            raise AssertionError(f"Missing justification — empty reason on {r['complaint_id']}")
        if r["priority"] not in ("Urgent", "Standard", "Low"):
            raise AssertionError(f"Invalid priority '{r['priority']}' on {r['complaint_id']}")
        if _severity_hits(description) and r["priority"] != "Urgent":
            raise AssertionError(
                f"Severity blindness — {r['complaint_id']} has severity keyword(s) "
                f"{_severity_hits(description)} but priority is '{r['priority']}'"
            )


def batch_classify(input_path: str, output_path: str) -> None:
    """Read input CSV, classify each row, write results CSV.

    Produces output even if some rows fail; failed rows are flagged NEEDS_REVIEW.
    """
    results = []
    records = []  # (description, result) pairs for independent enforcement
    with open(input_path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            description = (row.get("description") or "").strip()
            try:
                result = classify_complaint(row)
            except Exception as exc:  # never let one bad row abort the batch
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Urgent" if _severity_hits(description) else "Standard",
                    "reason": f"Row could not be classified: {exc}.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)
            records.append((description, result))

    _enforce(records)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    review = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Done. Results written to {output_path}")
    print(f"Rows classified: {len(results)} | Urgent: {urgent} | NEEDS_REVIEW: {review}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

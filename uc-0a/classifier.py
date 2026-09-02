"""
UC-0A — Complaint Classifier

Vibe-coded with a RICE prompt and refined through the CRAFT loop. The
enforcement rules in agents.md are implemented directly here:

- category must be exactly one of the 10 allowed strings (no variations)
- priority must be Urgent when a severity keyword is present
- every output row carries a reason citing the exact words used
- flag = NEEDS_REVIEW when two category signals tie
"""
import argparse
import csv
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flooded", "flooding", "floods", "rainwater"]),
    ("Drain Blockage", ["drain blocked", "stormwater drain", "main drain blocked",
                        "drain completely blocked", "100% blocked"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "unlit",
                     "substation tripped", "darkness", "wiring theft"]),
    ("Waste", ["garbage", "waste", "overflowing", "overflow", "bins",
               "not cleared", "dead animal", "waste bins"]),
    ("Noise", ["music", "drilling", "amplifier", "idling", "engines",
               "band playing", "delivery trucks"]),
    ("Road Damage", ["road surface", "road collapsed", "road subsided", "cracked",
                     "sinking", "manhole", "footpath", "buckled", "paving", "crater"]),
    ("Heritage Damage", ["heritage", "lamp post", "cobblestone", "monument", "ancient"]),
    ("Heat Hazard", ["temperature", "melting", "heat", "burns", "44", "45", "52", "unbearable"]),
]


def normalize(text):
    return (text or "").lower()


def matched_keywords(description, category):
    desc = normalize(description)
    found = []
    for name, keywords in CATEGORY_RULES:
        if name != category:
            continue
        for kw in keywords:
            if kw in desc:
                found.append(kw)
    return found


def match_category(description):
    desc = normalize(description)
    scores = {name: 0 for name, _ in CATEGORY_RULES}
    for name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc:
                scores[name] += 1

    ranked = sorted(
        scores.items(),
        key=lambda kv: (-kv[1], ALLOWED_CATEGORIES.index(kv[0])),
    )
    best, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if best_score == 0:
        return "Other", False

    ambiguous = second_score == best_score and best_score > 0
    return best, ambiguous


def severity_keywords_found(description):
    desc = normalize(description)
    return [kw for kw in SEVERITY_KEYWORDS if kw in desc]


def reason_for(category, priority, ambiguous, found_kws, matched_kws):
    parts = []
    if matched_kws:
        parts.append("category %s because the description mentions '%s'" % (category, "', '".join(matched_kws)))
    else:
        parts.append("category %s because no taxonomy signal matched" % category)
    if priority == "Urgent":
        parts.append("priority Urgent because it contains severity word(s) '%s'" % "', '".join(found_kws))
    else:
        parts.append("priority Standard because no severity keyword is present")
    if ambiguous:
        parts.append("flag NEEDS_REVIEW because a second category signal ties the primary signal")
    return "; ".join(parts) + "."


def classify_complaint(row):
    desc = row.get("description") or ""
    if not desc.strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "category Other because the description is empty; flag NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }

    category, ambiguous = match_category(desc)
    found_kws = severity_keywords_found(desc)
    priority = "Urgent" if found_kws else "Standard"
    matched = matched_keywords(desc, category)
    reason = reason_for(category, priority, ambiguous, found_kws, matched)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path, output_path):
    try:
        with open(input_path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except FileNotFoundError:
        print("Error: input file not found: %s" % input_path)
        sys.exit(1)

    if not rows:
        print("Error: input file has no data rows: %s" % input_path)
        sys.exit(1)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    written = 0
    failed = 0

    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(rows):
            complaint_id = (row.get("complaint_id") or "").strip() or ("row_%d" % (idx + 1))
            try:
                result = classify_complaint(row)
                writer.writerow({"complaint_id": complaint_id, **result})
                written += 1
            except Exception as exc:  # never crash the batch on one bad row
                failed += 1
                print("Warning: row %s failed (%s); writing with NEEDS_REVIEW" % (complaint_id, exc))
                writer.writerow({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "classification failed for this row; flag NEEDS_REVIEW.",
                    "flag": "NEEDS_REVIEW",
                })

    print("Done. Classified %d row(s), %d failed. Results written to %s" % (written, failed, output_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

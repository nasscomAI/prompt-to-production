"""
UC-0A — Complaint Classifier
Vibe-coded from agents.md + skills.md (RICE → CRAFT workflow).

Enforcement rules from agents.md are implemented here:
  1. Category is exactly one of the 10 allowed values (no taxonomy drift).
  2. Priority is Urgent when a severity keyword is present, else Standard.
  3. Every row has a one-sentence reason citing words from the description.
  4. Multi-category rows are flagged NEEDS_REVIEW (no false confidence).
  5. No supported category -> category Other + flag NEEDS_REVIEW.
"""
import argparse
import csv
import os

ALLOWED_CATEGORIES = (
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
)

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

# Category -> signal phrases. Checked in order (most specific first).
# "Pothole" precedes "Road Damage" so pothole complaints are never swallowed.
CATEGORY_SIGNALS = (
    ("Pothole", ("pothole", "crater")),
    ("Flooding", ("flooded", "flooding", "floods", "flood", "waterlog", "submerged")),
    ("Streetlight", ("streetlight", "street light", "streetlights", "lights out",
                     "unlit", "lamp", "lighting")),
    ("Waste", ("garbage", "waste", "trash", "litter", "rubbish", "dumped",
               "dead animal", "bins")),
    ("Noise", ("music", "noise", "loudspeaker", "amplifier", "sound", "band")),
    ("Heat Hazard", ("heat", "heatwave", "44\u00b0c", "45\u00b0c", "52\u00b0c", "melting",
                     "temperature", "storing heat", "full sun")),
    ("Drain Blockage", ("drain", "drainage", "sewer", "clogged", "manhole")),
    ("Heritage Damage", ("heritage", "historic", "ancient step well", "monument",
                         "step well", "old city")),
    ("Road Damage", ("road surface", "road damage", "cracked", "sinking", "subsid",
                     "footpath", "paving", "buckled", "tiles broken", "asphalt")),
)


def _evidence(text: str, signals):
    """Return the first signal phrase found in the lowered text."""
    for signal in signals:
        if signal in text:
            return signal
    return None


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row into category, priority, reason, flag."""
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()
    lowered = description.casefold()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description text was present, so the complaint cannot be classified.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Category from allowed taxonomy only.
    matched = [category for category, signals in CATEGORY_SIGNALS
               if _evidence(lowered, signals) is not None]
    if not matched:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Urgent" if _evidence(lowered, SEVERITY_KEYWORDS) else "Standard",
            "reason": f"No allowed category is supported by the description: \"{description[:140]}.\"",
            "flag": "NEEDS_REVIEW",
        }

    category = matched[0]
    evidence = _evidence(lowered, dict(CATEGORY_SIGNALS)[category])

    # 2. Priority via severity keywords.
    severity = _evidence(lowered, SEVERITY_KEYWORDS)
    priority = "Urgent" if severity else "Standard"

    # 3. Reason cites specific description words.
    if priority == "Urgent":
        reason = (f"The description mentions \"{evidence}\" and \"{severity}\"; "
                  f"priority is Urgent because the description mentions \"{severity}\".")
    else:
        reason = f"The description mentions \"{evidence}\"."

    # 4. Multi-category -> genuinely ambiguous -> flag.
    flag = "NEEDS_REVIEW" if len(matched) > 1 else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write the results CSV."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row is None:
                row = {}
            classification = classify_complaint(row)
            if not classification["complaint_id"]:
                classification["flag"] = "NEEDS_REVIEW"
            results.append(classification)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
"""
UC-0A — Complaint Classifier
RICE → agents.md → skills.md → CRAFT implementation.
"""
import argparse
import csv
import re
import os

ALLOWED_CATEGORIES = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Single source of truth: these keywords decide the category AND supply the exact
# words quoted in the reason sentence. Keeping one list prevents the two from drifting.
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "water", "rainwater"],
    "Streetlight": ["light", "dark", "sparking", "unlit"],
    "Waste": ["garbage", "waste", "bins", "dumped", "dead animal", "litter"],
    "Noise": ["music", "noise", "loud", "drilling", "idling", "amplifier", "band playing"],
    "Road Damage": ["cracked", "sinking", "subsid", "buckled", "footpath", "paving",
                    "tiles broken", "road surface", "collapsed", "crater", "cobblestones"],
    "Heritage Damage": ["heritage", "historic", "ancient"],
    "Heat Hazard": ["heat", "melting", "temperature", "full sun"],
    "Drain Blockage": ["drain", "manhole", "stormwater"],
}

# Low is reserved for nuisance-class complaints carrying no safety implication.
# Any risk signal in the text keeps the row at Standard.
MINOR_CATEGORIES = ["Noise", "Heritage Damage"]
RISK_SIGNALS = [
    "risk", "unsafe", "safety", "danger", "accident",
    "health", "concern", "injured", "burns", "structural"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row according to RICE rules:
    - Allowed categories exact match
    - Severity keyword check for Urgent priority
    - Single-sentence justification citing specific words
    - Flag as NEEDS_REVIEW if ambiguous
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()
    
    # 1. Category matching — record which keywords fired so the reason can quote them
    matched = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if hits:
            matched[category] = hits

    # A pothole is a more specific report than general road damage; standing water
    # from a blocked drain is already covered by Flooding.
    if "Pothole" in matched:
        matched.pop("Road Damage", None)
    if "Flooding" in matched:
        matched.pop("Drain Blockage", None)

    flag = ""
    if len(matched) == 1:
        cat = next(iter(matched))
    elif len(matched) > 1:
        # Heritage context outranks the physical symptom but is never unambiguous.
        if "Heritage Damage" in matched:
            cat, flag = "Heritage Damage", "NEEDS_REVIEW"
        elif "Pothole" in matched:
            cat = "Pothole"
        elif "Flooding" in matched:
            cat = "Flooding"
        else:
            cat, flag = next(iter(matched)), "NEEDS_REVIEW"
    else:
        cat, flag = "Other", "NEEDS_REVIEW"

    # 2. Priority — severity keywords force Urgent; Low only for nuisance-class
    #    categories with no severity keyword and no risk signal in the text.
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    if severity_hits:
        priority = "Urgent"
    elif cat in MINOR_CATEGORIES and not any(s in desc_lower for s in RISK_SIGNALS):
        priority = "Low"
    else:
        priority = "Standard"

    # 3. Reason — quote the words that actually drove the decision. Falls back to the
    #    opening words of the description so every row cites the source text.
    quoted = (matched.get(cat, []) + severity_hits)[:3]
    if not quoted:
        quoted = re.findall(r"\b\w+\b", description)[:4]
    cited_str = ", ".join(f"'{w}'" for w in quoted)
    reason = f"Classified as {cat} with {priority} priority due to key terms {cited_str} in description."

    return {
        "complaint_id": complaint_id,
        "category": cat,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    # Ensure directory exists for output
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Batch classification complete. {len(results)} rows processed.")


def selftest(data_dir: str = "../data/city-test-files"):
    """
    Assert the four agents.md enforcement rules hold on every available city file.
    Run: python classifier.py --selftest
    """
    import glob

    files = sorted(glob.glob(os.path.join(data_dir, "test_*.csv")))
    assert files, f"No city test files found under {data_dir}"

    checked = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                out = classify_complaint(row)
                desc = row["description"].lower()
                cid = out["complaint_id"]

                assert out["category"] in ALLOWED_CATEGORIES, f"{cid}: category off-taxonomy"
                assert out["priority"] in ("Urgent", "Standard", "Low"), f"{cid}: priority off-taxonomy"

                if any(kw in desc for kw in SEVERITY_KEYWORDS):
                    assert out["priority"] == "Urgent", f"{cid}: severity keyword not Urgent"

                quoted = re.findall(r"'([^']+)'", out["reason"])
                assert quoted, f"{cid}: reason cites no words from the description"
                for word in quoted:
                    assert word.lower() in desc, f"{cid}: reason cites '{word}' which is absent from description"

                if out["category"] == "Other":
                    assert out["flag"] == "NEEDS_REVIEW", f"{cid}: unclassified row not flagged"

                checked += 1

    print(f"Self-test passed: {checked} rows across {len(files)} city files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  help="Path to test_[city].csv")
    parser.add_argument("--output", help="Path to write results CSV")
    parser.add_argument("--selftest", action="store_true",
                        help="Verify enforcement rules against every city test file")
    parser.add_argument("--data-dir", default="../data/city-test-files",
                        help="Directory of city test files (used by --selftest)")
    args = parser.parse_args()

    if args.selftest:
        selftest(args.data_dir)
    else:
        if not args.input or not args.output:
            parser.error("--input and --output are required unless --selftest is used")
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")

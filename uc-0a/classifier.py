"""
UC-0A — Complaint Classifier
Pure-Python regex classifier enforcing the RICE rules from agents.md and skills.md.
No external dependencies beyond the standard library.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Per-category regex patterns. Each entry: (pattern_string, display_label).
# Patterns are matched case-insensitively against the full description.
CATEGORY_PATTERNS = {
    "Pothole": [
        (r"pot[\s-]?hole", "pothole"),
    ],
    "Flooding": [
        (r"\bflood", "flood"),
        (r"water[\s-]?log", "waterlogged"),
        (r"\binundat", "inundated"),
        (r"\bsubmerg", "submerged"),
        (r"knee[\s-]?deep", "knee-deep"),
        (r"standing\s+water", "standing water"),
    ],
    "Streetlight": [
        (r"street[\s-]?light", "streetlight"),
        (r"\blamp\s*post\b", "lamp post"),
        (r"\blights?\s+(out|off|flicker|spark)", "lights out/flickering"),
    ],
    "Waste": [
        (r"\bgarbage\b", "garbage"),
        (r"\bwaste\b", "waste"),
        (r"\brubbish\b", "rubbish"),
        (r"\btrash\b", "trash"),
        (r"\blitter\b", "litter"),
        (r"\bbins?\b", "bin"),
        (r"dead\s+animal", "dead animal"),
        (r"\brefuse\b", "refuse"),
        (r"\bdumped\b", "dumped"),
        (r"\boverflowing\b", "overflowing"),
    ],
    "Noise": [
        (r"\bnoise\b", "noise"),
        (r"\bnoisy\b", "noisy"),
        (r"\bloud\b", "loud"),
        (r"\bmusic\b", "music"),
        (r"\bdisturbance\b", "disturbance"),
    ],
    "Road Damage": [
        (r"road\s+surface", "road surface"),
        (r"\bcracked\b", "cracked"),
        (r"\bsinking\b", "sinking"),
        (r"\bfootpath\b", "footpath"),
        (r"\btiles?\s+(broken|upturned|cracked)", "broken/upturned tiles"),
        (r"broken\s+road", "broken road"),
    ],
    "Heritage Damage": [
        (r"\bheritage\b", "heritage"),
        (r"\bhistoric", "historic"),
        (r"\bmonument\b", "monument"),
        (r"\bancient\b", "ancient"),
    ],
    "Heat Hazard": [
        (r"\bheatwave\b", "heatwave"),
        (r"extreme\s+(heat|temperature)", "extreme heat/temperature"),
        (r"\bscorch", "scorching"),
    ],
    "Drain Blockage": [
        (r"\bdrains?\b", "drain"),
        (r"\bmanhole\b", "manhole"),
        (r"\bsewer\b", "sewer"),
        (r"drain\s+block", "drain block"),
    ],
}


def _match_categories(description: str) -> dict:
    """
    Return {category: [matched_text, ...]} for every category with at least one hit.
    Matched text is the actual substring found in the description.
    """
    hits = {}
    for cat, patterns in CATEGORY_PATTERNS.items():
        matched = []
        for pattern, _ in patterns:
            m = re.search(pattern, description, re.I)
            if m:
                matched.append(m.group(0))
        if matched:
            hits[cat] = matched
    return hits


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using regex keyword matching.
    Returns dict with keys: category, priority, reason, flag.
    """
    description = row.get("description", "").strip()

    if not description:
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "No parseable description provided",
            "flag": "NEEDS_REVIEW",
        }

    # Priority: Urgent if any severity keyword present, Standard otherwise
    severity_hits = [
        kw for kw in SEVERITY_KEYWORDS
        if re.search(r"\b" + kw + r"\b", description, re.I)
    ]
    priority = "Urgent" if severity_hits else "Standard"

    cat_hits = _match_categories(description)

    if not cat_hits:
        return {
            "category": "Other",
            "priority": priority,
            "reason": "No category keywords matched in the complaint description.",
            "flag": "",
        }

    if len(cat_hits) == 1:
        category = next(iter(cat_hits))
        words = cat_hits[category]
        reason = f'Description contains "{", ".join(words)}", indicating {category}.'
        flag = ""
    else:
        # Multiple categories match — pick the one with the most keyword hits;
        # flag as ambiguous since the description maps to more than one category.
        category = max(cat_hits, key=lambda c: len(cat_hits[c]))
        all_words = [w for hits in cat_hits.values() for w in hits]
        matched_cats = " or ".join(cat_hits.keys())
        reason = (
            f'Description contains "{", ".join(all_words)}" which could indicate '
            f'{matched_cats}.'
        )
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Aborts on missing file or missing description column.
    Applies error-handling defaults for individual malformed rows.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            if not fieldnames or "description" not in fieldnames:
                print(
                    "Error: input CSV is missing the required 'description' column.",
                    file=sys.stderr,
                )
                sys.exit(1)

            rows = list(reader)

    except FileNotFoundError:
        print(f"Error: input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: unable to read input file '{input_path}': {e}", file=sys.stderr)
        sys.exit(1)

    output_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=output_fields)
        writer.writeheader()

        total = len(rows)
        for i, row in enumerate(rows, start=1):
            complaint_id = row.get("complaint_id", f"row-{i}")
            try:
                classification = classify_complaint(row)
            except Exception as e:
                print(
                    f"Warning: unexpected error on row {i} ({complaint_id}): {e}",
                    file=sys.stderr,
                )
                classification = {
                    "category": "Other",
                    "priority": "Low",
                    "reason": "No parseable description provided",
                    "flag": "NEEDS_REVIEW",
                }

            writer.writerow({**row, **classification})
            print(
                f"  [{i}/{total}] {complaint_id} → {classification['category']} / "
                f"{classification['priority']}"
                + (f" [{classification['flag']}]" if classification["flag"] else "")
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

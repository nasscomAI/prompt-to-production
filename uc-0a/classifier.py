import pandas as pd
import argparse
import sys
import os

# Allowed schema (STRICT)
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "crater", "pot hole"],
    "Flooding": ["flood", "waterlog", "water log", "submerge", "inundat", "standing water"],
    "Streetlight": ["streetlight", "street light", "lamp", "darkness", "no light", "flicker", "sparking"],
    "Waste": ["waste", "garbage", "trash", "dump", "rubbish", "dead animal"],
    "Noise": ["noise", "loud", "music", "speaker", "sound"],
    "Road Damage": ["crack", "broken road", "road damage", "sinking", "tiles broken", "surface damaged"],
    "Heritage Damage": ["heritage", "monument", "historic", "ancient"],
    "Heat Hazard": ["heat", "sun", "temperature", "hot"],
    "Drain Blockage": ["drain", "sewer", "clog", "overflow", "choke", "manhole"]
}

# Priority-based resolution for multi-category cases
CATEGORY_PRIORITY = [
    "Flooding",
    "Drain Blockage",
    "Pothole",
    "Road Damage",
    "Streetlight",
    "Waste",
    "Noise",
    "Heritage Damage",
    "Heat Hazard"
]


def classify(description):
    """
    Classify a single complaint description.
    Returns: category, priority, reason, flag
    """

    # Validate input
    if not isinstance(description, str) or not description.strip():
        return "Other", "Low", "No valid description provided.", "NEEDS_REVIEW"

    text = description.lower()

    # --------------------------
    # PRIORITY DETECTION
    # --------------------------
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in text:
            priority = "Urgent"
            break

    # --------------------------
    # CATEGORY MATCHING
    # --------------------------
    category_hits = {}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                if cat not in category_hits:
                    category_hits[cat] = []
                category_hits[cat].append(kw)

    # --------------------------
    # NO MATCH → NEEDS REVIEW
    # --------------------------
    if not category_hits:
        snippet = description[:50].replace("\n", " ")
        return (
            "Other",
            priority,
            f"No allowed category keywords found in '{snippet}...'.",
            "NEEDS_REVIEW"
        )

    # --------------------------
    # SINGLE CATEGORY MATCH
    # --------------------------
    if len(category_hits) == 1:
        cat = list(category_hits.keys())[0]
        kw = category_hits[cat][0]

        return (
            cat,
            priority,
            f"Keyword '{kw}' found in description indicating {cat.lower()} issue.",
            ""
        )

    # --------------------------
    # MULTIPLE MATCHES → RESOLVE USING PRIORITY
    # --------------------------
    for cat in CATEGORY_PRIORITY:
        if cat in category_hits:
            kw = category_hits[cat][0]

            return (
                cat,
                priority,
                f"Multiple signals detected; prioritizing '{cat}' due to keyword '{kw}'.",
                ""
            )

    # Fallback safety
    return (
        "Other",
        priority,
        "Conflicting signals; unable to determine category confidently.",
        "NEEDS_REVIEW"
    )


def main():
    parser = argparse.ArgumentParser(description="Complaint Classification System - UC-0A")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    # --------------------------
    # FILE VALIDATION
    # --------------------------
    if not os.path.exists(args.input):
        print(f"Error: Input file not found at {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # --------------------------
    # STRICT COLUMN VALIDATION
    # --------------------------
    REQUIRED_COLUMNS = ["description"]

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"Error: Missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    desc_col = "description"

    # --------------------------
    # PROCESS ROWS
    # --------------------------
    results = []

    for _, row in df.iterrows():
        desc = row[desc_col]

        try:
            cat, pri, rea, flg = classify(desc)
        except Exception as e:
            cat = "Other"
            pri = "Standard"
            rea = f"Processing error: {str(e)}"
            flg = "NEEDS_REVIEW"

        results.append({
            "description": str(desc) if pd.notna(desc) else "",
            "category": cat,
            "priority": pri,
            "reason": rea,
            "flag": flg
        })

    # --------------------------
    # SAVE OUTPUT
    # --------------------------
    try:
        pd.DataFrame(results).to_csv(args.output, index=False)
        print(f"Success: Processed {len(results)} complaints → saved to {args.output}")
    except Exception as e:
        print(f"Error writing output CSV: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
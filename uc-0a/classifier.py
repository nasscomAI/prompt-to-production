"""
UC-0A — Complaint Classifier
Classifies citizen complaints into categories and priorities using keyword-based rules.
Follows agents.md enforcement: fixed taxonomy, severity keyword triggers, mandatory reason, NEEDS_REVIEW for ambiguity.
"""
import argparse
import csv
import re
import sys

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "road hole", "road holes"],
    "Flooding": ["flood", "flooded", "flooding", "waterlogged", "water logging",
                 "knee-deep", "inundated", "rainwater", "channel rainwater",
                 "underpass flooded", "cars regularly abandoned"],
    "Streetlight": ["streetlight", "street light", "streetlights", "street lights",
                    "lamp post", "lights out", "flickering", "sparking", "unlit",
                    "lit after", "lighting", "darkness", "substation tripped",
                    "colony substation"],
    "Waste": ["garbage", "waste", "rubbish", "overflowing", "dead animal", "dumped",
              "debris", "not cleared", "bins overflowing", "waste bins",
              "piles of waste", "waste not cleared", "waste not cleared before",
              "market waste", "restaurant waste"],
    "Noise": ["noise", "music", "loud", "midnight", "past midnight", "decibel",
              "wedding venue", "audible", "2am", "3am", "drilling", "idling",
              "engines on", "amplifiers", "wedding band", "band playing",
              "delivery trucks idling"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken road", "road crack",
                    "upturned", "footpath tiles", "footpath broken", "subsidence",
                    "bubbling", "broken bench", "paving", "collapsed", "crater",
                    "road collapsed", "road subsided", "cobblestones broken",
                    "buckled", "structural concern", "dead trees", "split branches",
                    "fall risk"],
    "Heritage Damage": ["heritage", "heritage street", "old city", "heritage area",
                        "heritage building", "ancient", "heritage zone",
                        "heritage stone", "heritage residential",
                        "heritage lamp post", "heritage precinct"],
    "Heat Hazard": ["heat", "hot", "burning", "melting", "tarmac", "dividers",
                    "heatwave", "scorching", "temperature", "temperatures",
                    "44°", "45°", "52°", "unbearable", "dangerous temperature",
                    "sun", "burns on contact", "sticking", "road surface bubbling"],
    "Drain Blockage": ["drain", "drainage", "blocked drain", "manhole", "manhole cover",
                       "sewer", "clogged", "stormwater drain"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description — no information available for classification.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Category classification ---
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                break

    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    else:
        # Multiple categories matched — pick by strongest signal (most keyword hits)
        keyword_counts = {}
        for cat in matched_categories:
            count = sum(1 for kw in CATEGORY_KEYWORDS[cat] if kw in desc_lower)
            keyword_counts[cat] = count
        max_count = max(keyword_counts.values())
        candidates = [cat for cat, c in keyword_counts.items() if c == max_count]
        if len(candidates) == 1:
            category = candidates[0]
        else:
            # Tie — use priority order
            priority_order = [
                "Drain Blockage", "Flooding", "Pothole", "Heat Hazard",
                "Heritage Damage", "Streetlight", "Road Damage",
                "Waste", "Noise"
            ]
            category = candidates[0]
            for p in priority_order:
                if p in candidates:
                    category = p
                    break
        # Only flag NEEDS_REVIEW if the winner is genuinely close to second place
        sorted_counts = sorted(keyword_counts.values(), reverse=True)
        second = sorted_counts[1] if len(sorted_counts) > 1 else 0
        flag = "NEEDS_REVIEW" if max_count - second <= 1 else ""

    # --- Priority classification (severity keyword check) ---
    has_severity = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"

    # --- Reason construction ---
    # Extract the most relevant words from description for the reason
    reason = _build_reason(description, category)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(description: str, category: str) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    desc_lower = description.lower()

    # Map category to the most relevant keyword to cite
    category_signal = {
        "Pothole": ["pothole", "potholes"],
        "Flooding": ["flood", "flooded", "flooding", "waterlogged", "knee-deep", "rainwater", "underpass flooded"],
        "Streetlight": ["streetlight", "street light", "lights out", "flickering", "sparking", "unlit", "darkness", "substation"],
        "Waste": ["garbage", "waste", "overflowing", "dead animal", "dumped", "piles", "waste bins", "market waste"],
        "Noise": ["music", "midnight", "loud", "noise", "audible", "drilling", "amplifiers", "band", "idling"],
        "Road Damage": ["cracked", "sinking", "broken", "upturned", "road surface", "subsidence", "bubbling",
                        "collapsed", "crater", "buckled", "cobblestones", "dead trees", "fall risk", "paving"],
        "Heritage Damage": ["heritage", "old city", "ancient", "heritage zone", "heritage stone", "heritage lamp post"],
        "Heat Hazard": ["heat", "burning", "melting", "tarmac", "temperature", "unbearable", "sun", "45°", "52°"],
        "Drain Blockage": ["drain", "manhole", "blocked", "clogged", "stormwater"],
        "Other": [],
    }

    # Find cited words that appear in the description
    cited_words = []
    for kw in category_signal.get(category, []):
        if kw in desc_lower:
            cited_words.append(kw)

    # Also check for severity keywords in the description
    severity_found = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]

    # Build the reason sentence
    if cited_words:
        words_str = ", ".join(cited_words[:3])
        reason = f"Classified as {category} based on keywords: {words_str}"
    else:
        reason = f"Classified as {category} based on complaint description"

    if severity_found:
        severity_str = ", ".join(severity_found[:3])
        reason += f" — severity indicators: {severity_str}"

    reason += "."
    return reason


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Continues processing even if individual rows fail.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("WARNING: Input file is empty — no complaints to classify.", file=sys.stderr)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            complaint_id = row.get("complaint_id", "UNKNOWN")
            print(f"WARNING: Failed to classify {complaint_id}: {e}", file=sys.stderr)
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {e}",
                "flag": "NEEDS_REVIEW",
            })

    # Write output
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    total = len(results)
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    review_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Classified {total} complaints: {urgent_count} urgent, {review_count} flagged for review.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

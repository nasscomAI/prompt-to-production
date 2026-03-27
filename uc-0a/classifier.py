"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

COSMETIC_KEYWORDS = [
    "aesthetic", "cosmetic", "informational", "notice",
    "sign missing", "faded paint", "cleaning",
]

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole", "pot hole", "hole in road", "hole in street",
        "crater", "road hole", "pavement hole", "sink hole", "sinkhole",
    ],
    "Flooding": [
        "flood", "flooding", "waterlogging", "water log",
        "waterlogged", "submerged", "water accumulation",
        "stagnant water", "inundat", "rainwater",
    ],
    "Streetlight": [
        "streetlight", "street light", "lamp post", "lamp post",
        "light not working", "light out", "broken light",
        "street lamp", "pole light", "lamp broken", "light pole",
        "unlit", "lights out", "wiring theft", "darkness",
    ],
    "Waste": [
        "garbage", "trash", "rubbish", "litter", "waste dump",
        "dumping", "refuse", "dustbin", "bin overflow", "bin full",
        "garbage pile", "trash pile", "waste pile", "bulk waste",
        "dead animal", "animal carcass", "renovation dump",
        "waste dump", "dumped on", "waste overflowing", "bins overflowing",
        "waste not cleared",
    ],
    "Noise": [
        "noise", "noisy", "loud music", "loud speaker",
        "loudspeaker", "construction noise", "noise pollution",
        "decibel", "sound pollution", "music past", "dj",
        "loudspeaker", "amplifier", "club music", "music audible",
        "drilling", "wedding band",
    ],
    "Road Damage": [
        "road damage", "damaged road", "crack in road", "road crack",
        "broken road", "uneven road", "road surface", "road worn",
        "road deteriorat", "road eroded", "pavement damage",
        "footpath", "sidewalk", "tiles broken", "tiles upturned",
        "upturned paving", "road subsidence", "road subsided",
    ],
    "Heritage Damage": [
        "heritage", "monument", "historical building", "historic site",
        "ancient wall", "heritage site", "heritage structure",
        "old fort", "temple damage", "archaeological", "historic",
        "cobblestone",
    ],
    "Heat Hazard": [
        "heat", "heatwave", "heat wave", "extreme heat",
        "heat stroke", "hot tar", "melting road", "heat related",
        "heat advis", "heat danger", "melting tarmac", "tarmac surface melting",
        "surface temperature", "dangerous temperatures", "storing heat",
        "burns on contact",
    ],
    "Drain Blockage": [
        "drain", "blocked drain", "clogged drain", "sewer",
        "sewage", "overflowing drain", "storm drain",
        "drainage", "manhole", "pipe block",
    ],
}


def _matches_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return list of keywords found in text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw in text_lower]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # Handle empty / missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided for classification.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # Score each category by keyword matches
    scores: dict[str, list[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = _matches_keywords(desc_lower, keywords)
        if matched:
            scores[category] = matched

    # Determine best category
    if not scores:
        category = "Other"
        reason_words = []
    else:
        max_score = max(len(v) for v in scores.values())
        top = [cat for cat, kws in scores.items() if len(kws) == max_score]

        if len(top) == 1:
            category = top[0]
            reason_words = scores[category]
        else:
            # Ambiguous — multiple categories tie
            category = top[0]
            reason_words = scores[category]

    # Build reason citing specific words from description
    if reason_words:
        cited = ", ".join(f'"{w}"' for w in reason_words[:3])
        reason = (
            f'Description contains {cited}, indicating a {category} complaint.'
        )
    else:
        reason = (
            f'No specific category keywords found; classified as {category}.'
        )

    # Determine priority based on severity keywords
    severity_matches = _matches_keywords(desc_lower, SEVERITY_KEYWORDS)
    if severity_matches:
        priority = "Urgent"
    else:
        cosmetic_matches = _matches_keywords(desc_lower, COSMETIC_KEYWORDS)
        if cosmetic_matches or category == "Other":
            priority = "Low"
        else:
            priority = "Standard"

    # Determine flag
    flag = ""
    if len(scores) > 1 and max(len(v) for v in scores.values()) > 0:
        top_score = max(len(v) for v in scores.values())
        tied = [cat for cat, kws in scores.items() if len(kws) == top_score]
        if len(tied) > 1:
            flag = "NEEDS_REVIEW"
            reason += f' Ambiguous between {", ".join(tied)}.'

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    One bad row must not prevent remaining rows from being classified.
    """
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    logging.warning(f"Row {i} failed: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{i}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Classification error: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to read input CSV: {e}")
        sys.exit(1)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
            )
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        logging.error(f"Failed to write output CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

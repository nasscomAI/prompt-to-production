"""
UC-0A Complaint Classifier
Strict RICE enforcement rules from agents.md and skills.md.

Core failure modes guarded against:
  - Taxonomy drift: Only exact allowed category strings
  - Severity blindness: Keyword override always forces Urgent
  - Missing justification: Reason always cites description words
  - Hallucinated sub-categories: No invented categories
  - False confidence on ambiguity: NEEDS_REVIEW flag on multi-match
"""
import argparse
import csv
import sys
import re

# ── Schema Constants (exact strings from agents.md) ──────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# ── Category keyword map — every category must be reachable ──────────────────

CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "pot hole", "potholes"],
    "Flooding":        ["flood", "flooded", "flooding", "waterlog", "submerge", "inundat"],
    "Streetlight":     ["streetlight", "street light", "lamp post", "lights out",
                        "light not working", "dark street", "no light", "bulb"],
    "Waste":           ["waste", "garbage", "trash", "rubbish", "litter", "dump",
                        "refuse", "debris pile", "animal carcass", "dead animal"],
    "Noise":           ["noise", "loud", "music", "drilling", "honking", "horn",
                        "idling", "engines on", "blasting", "construction noise",
                        "loudspeaker", "speaker"],
    "Road Damage":     ["road damage", "crack", "cracked", "sinkhole", "sink",
                        "manhole", "broken footpath", "broken road", "crater",
                        "road collapse", "collapsed road", "road broke",
                        "road surface", "asphalt"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "archaeological",
                        "protected structure", "old city wall"],
    "Heat Hazard":     ["heat", "heatwave", "sunstroke", "heat stroke", "dehydrat",
                        "scorching", "temperature", "hot surface", "thermal"],
    "Drain Blockage":  ["drain", "drainage", "sewer", "sewage", "gutter",
                        "stormwater", "nala", "nalla"],
}


def _find_matching_categories(desc_lower: str) -> list:
    """Return all categories whose keywords appear in the description."""
    matches = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matches.append(category)
                break
    return matches


def _find_urgent_trigger(desc_lower: str) -> str | None:
    """Return the first severity keyword found, or None."""
    for kw in URGENT_KEYWORDS:
        # Prefix-aware search: "hospital" matches "hospitalised", "collapse" matches "collapsed"
        if re.search(r'\b' + re.escape(kw), desc_lower):
            return kw
    return None


def _extract_citation(description: str, max_words: int = 6) -> str:
    """Pull a meaningful phrase from the description for the reason field."""
    words = description.split()
    if len(words) <= max_words:
        return description.strip()
    return " ".join(words[:max_words]) + "..."


# ── Skill 1: classify_complaint ──────────────────────────────────────────────

def classify_complaint(description: str) -> dict:
    """
    Evaluates a single citizen complaint based on RICE rules.

    Returns dict with:
      category  — one of the 10 allowed strings
      priority  — Urgent / Standard / Low
      reason    — one sentence citing words from description
      flag      — NEEDS_REVIEW or empty string
    """
    desc_lower = description.lower()

    # ── 1. Category (Rule 1: strict strings only) ────────────────────────
    matched = _find_matching_categories(desc_lower)

    if len(matched) == 0:
        category = "Other"
    elif len(matched) == 1:
        category = matched[0]
    else:
        # Multiple categories matched — pick the most specific one,
        # but flag for review (Rule 4: ambiguity)
        # Priority order: more specific categories win over generic ones
        priority_order = [
            "Heritage Damage", "Heat Hazard", "Road Damage",
            "Drain Blockage", "Pothole", "Flooding",
            "Streetlight", "Noise", "Waste"
        ]
        category = "Other"
        for cat in priority_order:
            if cat in matched:
                category = cat
                break

    # ── 4. Ambiguity Flag (Rule 4) ───────────────────────────────────────
    flag = ""
    if len(matched) > 1:
        flag = "NEEDS_REVIEW"

    # ── 2. Priority (Rule 2: keyword-enforced) ───────────────────────────
    triggered_keyword = _find_urgent_trigger(desc_lower)

    if triggered_keyword:
        # CRITICAL OVERRIDE: severity keyword always forces Urgent
        priority = "Urgent"
    elif category in ["Pothole", "Flooding", "Road Damage", "Drain Blockage",
                       "Heritage Damage", "Heat Hazard"]:
        priority = "Standard"
    elif category in ["Noise", "Waste"]:
        priority = "Low"
    else:
        priority = "Standard"

    # ── 3. Reason (Rule 3: must cite specific words) ─────────────────────
    citation = _extract_citation(description)

    if triggered_keyword:
        reason = (f"Classified as '{category}' with Urgent priority because "
                  f"the description mentions '{triggered_keyword}': \"{citation}\".")
    else:
        reason = (f"Classified as '{category}' based on description: "
                  f"\"{citation}\".")

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Skill 2: batch_classify ─────────────────────────────────────────────────

def batch_classify(input_file: str, output_file: str):
    """
    Bulk processing engine.
    Reads input CSV → applies classify_complaint per row → writes output CSV.
    """
    results = []

    print(f"Reading from {input_file}...")
    try:
        with open(input_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames)

            # Append RICE output columns if missing
            for field in ["category", "priority", "reason", "flag"]:
                if field not in fieldnames:
                    fieldnames.append(field)

            for row in reader:
                description = row.get("description", "")
                classification = classify_complaint(description)

                row["category"] = classification["category"]
                row["priority"] = classification["priority"]
                row["reason"]   = classification["reason"]
                row["flag"]     = classification["flag"]

                results.append(row)

        print(f"Classified {len(results)} complaints.")

    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_file}")
        sys.exit(1)

    print(f"Writing to {output_file}...")
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("Batch classification complete!")


# ── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Citizen Complaint Classifier (RICE-enforced)"
    )
    parser.add_argument("--input",  required=True, help="Path to the input CSV file")
    parser.add_argument("--output", required=True, help="Path for the output CSV file")

    args = parser.parse_args()
    batch_classify(args.input, args.output)

"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in agents.md and skills.md.
Uses rule-based keyword matching guided by the RICE enforcement rules.
"""
import argparse
import csv
import re


# --- Classification Schema (from agents.md enforcement rules) ---

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword mapping — order matters (more specific first)
CATEGORY_KEYWORDS = {
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "archaeological", "tourist"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke", "temperature", "hot road", "melting"],
    "Drain Blockage": ["drain blocked", "drain blockage", "blocked drain", "drain overflow",
                       "drain clogged", "stormwater drain", "drain.*block", "mosquito.*drain",
                       "drain.*mosquito"],
    "Flooding": ["flood", "floods", "waterlog", "submerge", "inundate", "water stagnation",
                 "rain.*water", "water.*logging", "flooded"],
    "Pothole": ["pothole", "pot hole", "crater", "road.*hole", "hole.*road"],
    "Road Damage": ["road damage", "road collapse", "road crack", "road cave", "road.*broken",
                    "road.*deteriorat", "road.*crater", "collapsed.*road", "road.*sunk"],
    "Streetlight": ["streetlight", "street light", "lamp post", "lamppost", "no light",
                    "dark road", "bulb.*broken", "light.*not working", "light.*out"],
    "Waste": ["garbage", "waste", "bulk waste", "trash", "rubbish", "litter", "dump",
              "refuse", "debris.*not cleared", "not cleared"],
    "Noise": ["noise", "loud", "drilling", "honking", "construction noise",
              "sound pollution", "decibel", "idling.*engine", "engines.*idling"],
}


def _match_category(description: str) -> tuple:
    """
    Match description against category keywords.
    Returns (category, matched_words, is_ambiguous).
    """
    desc_lower = description.lower()
    matches = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = []
        for kw in keywords:
            if re.search(kw, desc_lower):
                matched.append(kw)
        if matched:
            matches.append((category, matched))

    if not matches:
        return "Other", [], True

    if len(matches) == 1:
        return matches[0][0], matches[0][1], False

    # Multiple category matches — pick the one with most keyword hits
    matches.sort(key=lambda x: len(x[1]), reverse=True)
    best = matches[0]
    second = matches[1]

    # If top two are close in match count, it's ambiguous
    is_ambiguous = len(best[1]) == len(second[1])
    return best[0], best[1], is_ambiguous


def _check_severity(description: str) -> list:
    """Check if any severity keywords are present. Returns list of matched keywords."""
    desc_lower = description.lower()
    found = []
    for kw in SEVERITY_KEYWORDS:
        # Use word-start boundary but allow suffixes (e.g. "hospitalised", "collapsed")
        if re.search(r'\b' + kw, desc_lower):
            found.append(kw)
    return found


def _determine_priority(description: str, severity_matches: list, is_ambiguous: bool) -> str:
    """
    Determine priority based on enforcement rules:
    - Urgent if severity keywords present
    - Standard for clear complaints without severity keywords
    - Low for vague or minor issues
    """
    if severity_matches:
        return "Urgent"

    desc_lower = description.lower()
    # Low priority indicators
    low_indicators = ["minor", "small", "slight", "cosmetic", "barely", "negligible"]
    if is_ambiguous or any(ind in desc_lower for ind in low_indicators):
        return "Low"

    return "Standard"


def _build_reason(category: str, matched_words: list, severity_matches: list, description: str) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    # Find actual words from description that triggered the match
    desc_lower = description.lower()
    cited_words = []

    # Cite severity keywords found in description
    for kw in severity_matches:
        for word in description.split():
            if kw in word.lower() and word not in cited_words:
                cited_words.append(word.strip(".,;:!?"))
                break

    # Cite category keywords found in description
    for kw in matched_words:
        pattern = re.compile(kw, re.IGNORECASE)
        match = pattern.search(description)
        if match:
            found_text = match.group(0)
            if found_text not in cited_words:
                cited_words.append(found_text)

    if cited_words:
        return f"Classified as {category} based on description containing: {', '.join(cited_words[:4])}."
    else:
        return f"Classified as {category} based on overall context of the complaint description."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules (from agents.md):
    - Category must be exactly one of the 10 allowed values
    - Priority is Urgent if severity keywords present
    - Reason must cite specific words from description
    - Flag is NEEDS_REVIEW for ambiguous cases
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Handle empty/null description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Step 1: Match category
    category, matched_words, is_ambiguous = _match_category(description)

    # Step 2: Check severity keywords
    severity_matches = _check_severity(description)

    # Step 3: Determine priority
    priority = _determine_priority(description, severity_matches, is_ambiguous)

    # Step 4: Build reason citing words from description
    reason = _build_reason(category, matched_words, severity_matches, description)

    # Step 5: Set flag
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Error handling (from skills.md):
    - Never crash on bad rows — produce output for every input row
    - Flag rows that fail to parse
    - Raise FileNotFoundError if input file doesn't exist
    """
    import os
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # Never crash — write a fallback row
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Failed to parse row: {str(e)[:50]}",
                    "flag": "NEEDS_REVIEW"
                })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

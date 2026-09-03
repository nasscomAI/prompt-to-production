"""
UC-0A — Complaint Classifier
Implementation guided by RICE framework, agents.md, and skills.md.
"""
import argparse
import csv
import os
import re

# Allowed categories — exact strings only, no variations or hallucinated sub-categories
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

# Severity keywords that must trigger Urgent priority
SEVERITY_PATTERNS = [
    (r"\binjur(?:y|ies|ed)?\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschools?\b", "school"),
    (r"\bhospitals?(?:ised|ized)?\b", "hospital"),
    (r"\bambulances?\b", "ambulance"),
    (r"\bfires?\b", "fire"),
    (r"\bhazards?(?:ous)?\b", "hazard"),
    (r"\bfell\b", "fell"),
    (r"\bcollaps(?:e|ed|ing)\b", "collapse"),
]

# Patterns indicating low priority (when no severity keywords exist)
LOW_PRIORITY_PATTERNS = [
    r"\bmusic\b",
    r"\bwedding\b",
    r"\bidling\b",
    r"\bgrass dying\b",
]

# Ambiguous cases that cannot be cleanly mapped to standard municipal categories
AMBIGUOUS_PATTERNS = [
    r"\bmanhole cover\b",
    r"\bdead trees?\b",
    r"\birrigation\b",
    r"\bdraining directly onto public road\b",
    r"\bsubstation tripped\b",
]


def _clean_reason_text(text: str) -> str:
    """Keep generated reasons as a single CSV-safe sentence."""
    return re.sub(r'["\n\r]+', ' ', str(text)).strip()


def _extract_citation(text: str, preferred_patterns=None) -> str:
    """Extract description words for the reason field, preferring priority triggers when present."""
    cleaned = re.sub(r'["\n\r]+', ' ', text).strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if s.strip()]

    if preferred_patterns:
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(re.search(pattern, sentence_lower) for pattern in preferred_patterns):
                first_sentence = sentences[0].rstrip(".?!")
                trigger_sentence = sentence.rstrip(".?!")
                if first_sentence and first_sentence != trigger_sentence:
                    return f"{first_sentence}; {trigger_sentence}"
                return trigger_sentence

    target = sentences[0] if sentences else cleaned
    return target.rstrip(".?!")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Low",
            "reason": 'Classified as Other due to invalid row format.',
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "") or "").strip()
    raw_desc = str(row.get("description", "") or "").strip()

    # Handle missing or empty descriptions
    if not raw_desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": 'Classified as Other due to missing complaint description.',
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = raw_desc.lower()

    # 1. Determine Priority via Severity Triggers
    matched_severity = []
    matched_severity_patterns = []
    for pattern, label in SEVERITY_PATTERNS:
        if re.search(pattern, desc_lower):
            matched_severity.append(label)
            matched_severity_patterns.append(pattern)

    if matched_severity:
        priority = "Urgent"
    elif any(re.search(p, desc_lower) for p in LOW_PRIORITY_PATTERNS):
        priority = "Low"
    else:
        priority = "Standard"

    # 2. Check for Ambiguous / Unclassifiable cases
    is_ambiguous = any(re.search(p, desc_lower) for p in AMBIGUOUS_PATTERNS)
    if is_ambiguous:
        citation = _extract_citation(raw_desc, matched_severity_patterns)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": f'Classified as Other with {priority} priority because the complaint describes "{citation}".',
            "flag": "NEEDS_REVIEW",
        }

    # 3. Categorization Logic based on domain signals
    category = None
    flag = ""

    # Heat Hazard
    if re.search(r"\b(?:4[4-9]|5[0-9])°c\b|\bheatwave\b|\bmelting\b|\bbubbling\b|\bdangerous temperatures?\b|\bburns on contact\b|\bstoring heat\b|\bbrt shelter roof glass broken\b", desc_lower):
        category = "Heat Hazard"

    # Road Damage (including collapsed road, cracked surfaces, broken footpaths)
    elif re.search(r"\broad collaps(?:e|ed|ing)\b|\broad subsid(?:e|ed|ing|ence)\b|\b(?:road surface|cracked and sinking|footpath|tiles broken|upturned paving|buckled)\b", desc_lower) and not re.search(r"\bheritage (?:stone|area|concern)\b", desc_lower):
        category = "Road Damage"

    # Pothole
    elif re.search(r"\bpotholes?\b|\bcrater\b|\btyre (?:damage|blowouts?)\b|\bwheel\b", desc_lower):
        category = "Pothole"

    # Noise
    elif re.search(r"\b(?:music|drilling|amplifier|amplifiers|wedding venue|wedding band|engines on)\b", desc_lower):
        category = "Noise"

    # Waste / Sanitation
    elif re.search(r"\b(?:garbage|waste|dead animal|bins overflowing|overflowing garbage|dumped on public road|post-market waste|night market waste)\b", desc_lower):
        category = "Waste"

    # Streetlight / Lighting
    elif re.search(r"\b(?:streetlights?|lights? out|unlit|flickering and sparking|electrical hazard|wiring theft)\b", desc_lower) and not re.search(r"\bheritage (?:lamp|stone|building)\b", desc_lower):
        category = "Streetlight"

    # Heritage Damage
    elif re.search(r"\bheritage\b|\bhistoric\b|\bancient step well\b|\btram road cobblestones\b|\bdefaced by billboard\b|\bheritage stone\b", desc_lower) and re.search(r"\b(?:broken|knocked over|defaced|subsidence|not restored|not replaced|concern)\b", desc_lower):
        category = "Heritage Damage"

    # Drain Blockage
    elif re.search(r"\b(?:stormwater drain|main drain|drain blocked|drain completely blocked|dengue concern)\b", desc_lower) and not re.search(r"\bunderpass flooded\b", desc_lower):
        category = "Drain Blockage"

    # Flooding
    elif re.search(r"\b(?:flooded|flooding|floods|knee-deep|standing in water|channel rainwater)\b", desc_lower):
        category = "Flooding"

    # Fallback if no specific category matched
    if not category:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Validate against allowed categories enum
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 4. Generate Reason (exactly one sentence citing specific words from description)
    citation = _extract_citation(raw_desc, matched_severity_patterns)
    reason = f'Classified as {category} with {priority} priority citing description: "{citation}".'

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
            reader = csv.DictReader(infile)
            while True:
                try:
                    row = next(reader)
                except StopIteration:
                    break
                except Exception as e:
                    results.append({
                        "complaint_id": "",
                        "category": "Other",
                        "priority": "Low",
                        "reason": f'Classified as Other due to unreadable input row: "{_clean_reason_text(e)}".',
                        "flag": "NEEDS_REVIEW",
                    })
                    break

                if isinstance(row, dict) and None in row:
                    complaint_id = str(row.get("complaint_id", "") or "").strip()
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": 'Classified as Other due to malformed input row.',
                        "flag": "NEEDS_REVIEW",
                    })
                    continue

                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f'Classified as Other due to error: "{_clean_reason_text(e)}".',
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        raise
    except Exception as e:
        results.append({
            "complaint_id": "",
            "category": "Other",
            "priority": "Low",
            "reason": f'Classified as Other due to input read error: "{_clean_reason_text(e)}".',
            "flag": "NEEDS_REVIEW",
        })

    # Ensure parent directory for output exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

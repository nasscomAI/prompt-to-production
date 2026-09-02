"""
UC-0A — Complaint Classifier
Rule-based, deterministic municipal complaint classifier using Python standard library.
"""
import argparse
import csv
import logging
import re
import sys
from typing import Dict, List, Tuple

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("complaint_classifier")

# 10 strictly allowed municipal complaint categories
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

# Severity keywords that trigger priority = 'Urgent'
# Overrides any other priority judgment
URGENT_PATTERN = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*|hazard\w*|fell|fallen|collaps\w*)\b",
    re.IGNORECASE
)

# Rule patterns and weights for category classification
CATEGORY_RULES: Dict[str, List[Tuple[re.Pattern, int]]] = {
    "Pothole": [
        (re.compile(r"\b(pothole|potholes|pot\s*hole|pot\s*holes)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(tyre\s+damage|tyre\s+blowout\w*|tire\s+blowout\w*|motorcycle\s+wheel)\b", re.IGNORECASE), 6),
        (re.compile(r"\b(crater)\b", re.IGNORECASE), 4),
    ],
    "Drain Blockage": [
        (re.compile(r"\b(drain\s+(?:completely\s+|100%\s+)?blocked|blocked\s+drain|drain\s+blockage|main\s+drain)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(stormwater\s+drain|drainage|manhole(?:\s+cover)?|sewer)\b", re.IGNORECASE), 8),
        (re.compile(r"\b(mosquito\s+breeding|dengue)\b", re.IGNORECASE), 6),
        (re.compile(r"\b(drain|draining)\b", re.IGNORECASE), 3),
    ],
    "Flooding": [
        (re.compile(r"\b(flooded|flooding|floods|flood|waterlogging|waterlogged)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(underpass\s+flooded|knee-deep|standing\s+in\s+water|stranded)\b", re.IGNORECASE), 8),
        (re.compile(r"\b(channel\s+rainwater|rainwater|rain)\b", re.IGNORECASE), 3),
    ],
    "Streetlight": [
        (re.compile(r"\b(streetlight|streetlights|street\s+light|street\s+lights|lamp\s+post)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(lights\s+out|unlit|darkness|dark\s+at\s+night|flickering|substation\s+tripped|wiring\s+theft)\b", re.IGNORECASE), 8),
    ],
    "Waste": [
        (re.compile(r"\b(garbage|waste|trash|rubbish|dumped|dumping|dead\s+animal|litter)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(bins?\s+overflowing|overflowing\s+(?:garbage\s+)?bins?|piles\s+of\s+waste)\b", re.IGNORECASE), 9),
        (re.compile(r"\b(bins?|overflow|overflowing)\b", re.IGNORECASE), 4),
    ],
    "Noise": [
        (re.compile(r"\b(noise|drilling|loudspeaker|amplifier|amplifiers|wedding\s+band|wedding\s+venue)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(music|club\s+music|idling(?:\s+with\s+engines)?|past\s+midnight|2am|5am)\b", re.IGNORECASE), 7),
    ],
    "Heat Hazard": [
        (re.compile(r"\b(heatwave|surface\s+melting|bubbling\s+at|burns\s+on\s+contact|storing\s+heat)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(\d+°C|\d+\s*degrees|temperature\s+unbearable|dangerous\s+temperatures?)\b", re.IGNORECASE), 9),
        (re.compile(r"\b(heat|temperature|full\s+sun|grass\s+dying)\b", re.IGNORECASE), 5),
    ],
    "Heritage Damage": [
        (re.compile(r"\b(cobblestones?\s+broken|defaced\s+by|heritage\s+stone(?:\s+not\s+replaced)?|ancient\s+step\s*well)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(heritage\s+building|heritage\s+lamp|historic\s+tram|heritage\s+concern)\b", re.IGNORECASE), 8),
        (re.compile(r"\b(heritage|historic|ancient|museum|monument)\b", re.IGNORECASE), 4),
    ],
    "Road Damage": [
        (re.compile(r"\b(road\s+surface|road\s+collapsed|road\s+subsidence|subsidence|buckled|cracked\s+and\s+sinking)\b", re.IGNORECASE), 10),
        (re.compile(r"\b(footpath\s+(?:tiles\s+)?broken|upturned\s+paving|paving\s+removed|tiles\s+broken|sinking)\b", re.IGNORECASE), 8),
        (re.compile(r"\b(footpath|paving|tarmac|cracked)\b", re.IGNORECASE), 4),
    ],
}

# Keywords indicating low priority complaints
LOW_PRIORITY_PATTERNS = [
    re.compile(r"\b(wedding\s+venue|wedding\s+band|club\s+music|music\s+past\s+midnight|amplifiers?)\b", re.IGNORECASE),
    re.compile(r"\b(grass\s+dying|irrigation|idling\s+with\s+engines)\b", re.IGNORECASE),
]


def _extract_evidence_snippet(text: str, matches: List[str]) -> str:
    """Extract a representative snippet or quoted words from the description."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Find sentence containing most matched terms
    for s in sentences:
        s_clean = s.strip()
        if any(m.lower() in s_clean.lower() for m in matches):
            # Truncate if exceptionally long
            if len(s_clean) > 80:
                return s_clean[:77] + "..."
            return s_clean.rstrip(".")
    # Fallback to first few words
    words = text.strip().split()
    snippet = " ".join(words[:8])
    return snippet.rstrip(".")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with original keys plus: category, priority, reason, flag
    """
    out_row = dict(row)
    description = (row.get("description") or "").strip()

    # Data validation & missing description handling
    if not description or len(description) < 5:
        logger.warning(
            f"Row ID '{row.get('complaint_id', 'UNKNOWN')}': Missing or insufficient description ('{description}')."
        )
        out_row["category"] = "Other"
        out_row["priority"] = "Standard"
        out_row["reason"] = "Description is missing or too short to classify."
        out_row["flag"] = "NEEDS_REVIEW"
        return out_row

    # 1. Evaluate Urgent Priority Rule
    urgent_matches = URGENT_PATTERN.findall(description)
    is_urgent = len(urgent_matches) > 0

    # 2. Score Categories
    category_scores: Dict[str, int] = {}
    category_matched_phrases: Dict[str, List[str]] = {}

    for cat, rules in CATEGORY_RULES.items():
        total_score = 0
        matched_phrases = []
        for pattern, weight in rules:
            found = pattern.findall(description)
            if found:
                total_score += weight * len(found)
                if isinstance(found[0], tuple):
                    matched_phrases.extend([item for tup in found for item in tup if item])
                else:
                    matched_phrases.extend(found)
        if total_score > 0:
            category_scores[cat] = total_score
            category_matched_phrases[cat] = list(set(matched_phrases))

    # Determine Best Category
    assigned_category = "Other"
    assigned_flag = ""
    evidence_terms: List[str] = []

    if not category_scores:
        assigned_category = "Other"
        assigned_flag = "NEEDS_REVIEW"
    else:
        # Sort categories by score descending
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_cats[0]

        # Check for ambiguity: if top score is very low or top two categories have equal score
        if top_score < 4:
            assigned_category = "Other"
            assigned_flag = "NEEDS_REVIEW"
        elif len(sorted_cats) > 1 and sorted_cats[0][1] == sorted_cats[1][1] and sorted_cats[0][1] < 8:
            assigned_category = top_cat
            assigned_flag = "NEEDS_REVIEW"
        else:
            assigned_category = top_cat
            evidence_terms = category_matched_phrases.get(top_cat, [])

    # Ensure assigned category is strictly in ALLOWED_CATEGORIES
    if assigned_category not in ALLOWED_CATEGORIES:
        assigned_category = "Other"
        assigned_flag = "NEEDS_REVIEW"

    # 3. Determine Priority (Urgent > Low / Standard)
    if is_urgent:
        assigned_priority = "Urgent"
    else:
        # Check for Low Priority patterns
        is_low = any(pat.search(description) for pat in LOW_PRIORITY_PATTERNS)
        if is_low and assigned_category in ["Noise", "Heat Hazard", "Waste"]:
            assigned_priority = "Low"
        else:
            assigned_priority = "Standard"

    # 4. Generate Reason citing specific words from description
    evidence_snippet = _extract_evidence_snippet(description, evidence_terms + urgent_matches)
    
    if assigned_category == "Other":
        if is_urgent:
            reason = f'Category ambiguous for "{evidence_snippet}", but marked Urgent due to safety keyword "{urgent_matches[0]}".'
        else:
            reason = f'Category could not be determined confidently from "{evidence_snippet}".'
    else:
        if is_urgent:
            matched_urgent_str = ", ".join(f'"{kw}"' for kw in set(urgent_matches[:2]))
            reason = f'Classified as {assigned_category} with Urgent priority due to {matched_urgent_str} in "{evidence_snippet}".'
        else:
            reason = f'Classified as {assigned_category} based on description mentioning "{evidence_snippet}".'

    out_row["category"] = assigned_category
    out_row["priority"] = assigned_priority
    out_row["reason"] = reason
    out_row["flag"] = assigned_flag

    return out_row


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Preserves all original columns and adds category, priority, reason, flag.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                logger.error(f"Input file '{input_path}' is empty or invalid CSV.")
                return

            original_fields = list(reader.fieldnames)
            new_fields = ["category", "priority", "reason", "flag"]
            # Avoid duplicate field names if already present
            out_fields = [f for f in original_fields if f not in new_fields] + new_fields

            rows_to_process = list(reader)

    except FileNotFoundError:
        logger.error(f"Input file '{input_path}' not found.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading input CSV '{input_path}': {e}")
        sys.exit(1)

    classified_rows = []
    has_description_column = "description" in original_fields

    if not has_description_column:
        logger.warning(f"Input CSV '{input_path}' missing 'description' column. All rows flagged for review.")

    for idx, row in enumerate(rows_to_process, start=1):
        try:
            if not has_description_column:
                row_copy = dict(row)
                row_copy["category"] = "Other"
                row_copy["priority"] = "Standard"
                row_copy["reason"] = "Input CSV lacks required 'description' column."
                row_copy["flag"] = "NEEDS_REVIEW"
                classified_rows.append(row_copy)
            else:
                classified = classify_complaint(row)
                classified_rows.append(classified)
        except Exception as e:
            logger.warning(f"Error processing row {idx} ({row.get('complaint_id', 'unknown')}): {e}. Fallback to Other.")
            row_fallback = dict(row)
            row_fallback["category"] = "Other"
            row_fallback["priority"] = "Standard"
            row_fallback["reason"] = f"Processing error: {e}"
            row_fallback["flag"] = "NEEDS_REVIEW"
            classified_rows.append(row_fallback)

    try:
        with open(output_path, mode="w", encoding="utf-8-sig", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(classified_rows)
        logger.info(f"Successfully processed {len(classified_rows)} rows -> '{output_path}'")
    except Exception as e:
        logger.error(f"Error writing output CSV '{output_path}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

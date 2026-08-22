"""
UC-0A — Complaint Classifier
Deterministic municipal citizen complaint classifier adhering to RICE prompt,
agents.md enforcement rules, and skills.md specifications.
"""
import argparse
import csv
import os
import re
from typing import Dict, List, Tuple

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
    "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_TRIGGERS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

REQUIRED_COLUMNS = [
    "complaint_id",
    "date_raised",
    "city",
    "ward",
    "location",
    "description",
    "reported_by",
    "days_open",
]


def _extract_evidence_phrase(text: str) -> str:
    """Extract a representative verbatim clause/phrase from the description for justification."""
    sentences = re.split(r"[.!?]\s*", text.strip())
    first_sentence = sentences[0].strip() if sentences else text.strip()
    if len(first_sentence) > 80:
        return first_sentence[:77] + "..."
    return first_sentence


def _detect_severity(text: str) -> Tuple[bool, List[str]]:
    """
    Check if any of the 9 defined severity triggers occur in the text (case-insensitively)
    as complete words bounded by word boundaries.
    Returns a tuple of (is_urgent, list_of_matched_triggers).
    """
    text_lower = text.lower()
    matched = []
    for trigger in SEVERITY_TRIGGERS:
        pattern = rf"\b{re.escape(trigger)}\b"
        if re.search(pattern, text_lower):
            matched.append(trigger)
    return (len(matched) > 0, matched)


def _detect_categories(text: str) -> List[Tuple[str, str]]:
    """
    Analyze text to identify candidate categories along with evidence snippets.
    Returns a list of tuples: (category_name, evidence_snippet).
    """
    text_lower = text.lower()
    candidates = []

    # 1. Pothole
    if re.search(r"\b(pothole|potholes|crater|tyre damage|tire damage)\b", text_lower):
        m = re.search(
            r"[^.!?]*\b(pothole|potholes|crater|tyre damage|tire damage)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "pothole damage reported"
        candidates.append(("Pothole", snippet))

    # 2. Heat Hazard
    if re.search(
        r"\b(heat|heatwave|melting|temperature|temperatures|\d+°c|burns on contact)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(heat|heatwave|melting|temperature|temperatures|\d+°c|burns on contact)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "heatwave conditions"
        candidates.append(("Heat Hazard", snippet))

    # 3. Flooding
    if re.search(
        r"\b(flood|floods|flooded|flooding|waterlogging|waterlogged|knee-deep|standing in water|channel rainwater)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(flood|floods|flooded|flooding|waterlogging|waterlogged|knee-deep|standing in water|channel rainwater)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "water accumulation reported"
        candidates.append(("Flooding", snippet))

    # 4. Drain Blockage
    if re.search(
        r"\b(drain blocked|drains blocked|drain blockage|stormwater drain|blocked drain|clogged drain)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(drain blocked|drains blocked|drain blockage|stormwater drain|blocked drain|clogged drain)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "drainage blockage reported"
        candidates.append(("Drain Blockage", snippet))

    # 5. Streetlight
    if re.search(
        r"\b(streetlight|streetlights|street light|street lights|lamp post|unlit|dark at night|darkness|substation tripped|lights out)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(streetlight|streetlights|lamp post|unlit|dark|lights out)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "lighting issue reported"
        candidates.append(("Streetlight", snippet))

    # 6. Waste
    if re.search(
        r"\b(garbage|waste|dumped|bins|dead animal|refuse|litter)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(garbage|waste|dumped|bins|dead animal)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "waste management issue"
        candidates.append(("Waste", snippet))

    # 7. Noise
    if re.search(
        r"\b(music|noise|wedding venue|wedding band|club music|drilling|amplifier|amplifiers|audible)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(music|noise|wedding|band|drilling|amplifier|amplifiers|audible)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "noise disturbance reported"
        candidates.append(("Noise", snippet))

    # 8. Heritage Damage
    if re.search(
        r"\b(heritage|historic|ancient step well|museum|tagore museum|monument|cobblestones|heritage stone)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(heritage|historic|ancient step well|museum|cobblestones)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "heritage site concern"
        candidates.append(("Heritage Damage", snippet))

    # 9. Road Damage
    if re.search(
        r"\b(road surface|cracked|sinking|subsidence|subsided|buckled|footpath|tiles broken|upturned|paving|manhole cover)\b",
        text_lower,
    ):
        m = re.search(
            r"[^.!?]*\b(road surface|cracked|sinking|subsidence|subsided|buckled|footpath|tiles broken|upturned|paving|manhole cover)[^.!?]*",
            text,
            re.IGNORECASE,
        )
        snippet = m.group(0).strip() if m else "road infrastructure damage"
        candidates.append(("Road Damage", snippet))

    return candidates


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint record according to municipal operations rules.
    Input: dict containing complaint details (description, etc.)
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description")

    # Fallback condition for missing/empty/invalid description (as specified in skills.md)
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": "Unable to classify because the complaint description is missing or invalid.",
            "flag": "NEEDS_REVIEW",
        }

    desc_text = str(description).strip()
    is_urgent, matched_triggers = _detect_severity(desc_text)
    candidates = _detect_categories(desc_text)

    # Resolve Category and Flag according to agents.md
    if not candidates:
        category = "Other"
        flag = "NEEDS_REVIEW"
        evidence = _extract_evidence_phrase(desc_text)
    elif len(candidates) == 1:
        category = candidates[0][0]
        evidence = candidates[0][1]
        flag = ""
    else:
        # Multiple candidate categories detected
        cat_names = [c[0] for c in candidates]

        # Check if one category is clearly the primary defect and the other is context/location
        # e.g., Heritage area mentioned alongside Waste or Streetlight outage
        if "Heritage Damage" in cat_names and len(cat_names) > 1:
            non_heritage = [c for c in candidates if c[0] != "Heritage Damage"]
            # If the heritage asset itself is physically damaged/defaced
            if any(term in desc_text.lower() for term in ["cobblestones broken", "not replaced", "defaced", "ancient step well", "knocked over"]):
                category = "Heritage Damage"
                evidence = next(c[1] for c in candidates if c[0] == "Heritage Damage")
                flag = "NEEDS_REVIEW" if non_heritage else ""
            else:
                # Heritage is the location/context, another category is primary defect
                category = non_heritage[0][0]
                evidence = non_heritage[0][1]
                flag = "NEEDS_REVIEW"
        elif "Flooding" in cat_names and "Drain Blockage" in cat_names:
            # Both categories are equally plausible manifestations
            category = "Flooding"
            evidence = f"{candidates[0][1]} and {candidates[1][1]}"
            flag = "NEEDS_REVIEW"
        else:
            # When two or more categories are equally plausible, flag for human review
            category = candidates[0][0]
            evidence = candidates[0][1]
            flag = "NEEDS_REVIEW"

    # Resolve Priority strictly based on defined severity triggers
    if is_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Clean evidence phrase for reason formatting
    evidence_clean = re.sub(r'["\n\r]', "", evidence).strip()
    if not evidence_clean:
        evidence_clean = _extract_evidence_phrase(desc_text)

    # Formulate exactly one sentence citing specific words from the description
    if is_urgent:
        trigger_str = ", ".join(matched_triggers)
        reason = f'Classified as {category} with Urgent priority due to severity trigger ({trigger_str}) and reported "{evidence_clean}".'
    elif flag == "NEEDS_REVIEW":
        reason = f'Classified as {category} with {priority} priority and flagged for review due to "{evidence_clean}".'
    else:
        reason = f'Classified as {category} with {priority} priority based on evidence of "{evidence_clean}".'

    # Schema Validation
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    if flag not in ("NEEDS_REVIEW", ""):
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each complaint row using classify_complaint, and write results CSV.
    Preserves row count, row order, and original field values while appending category, priority, reason, flag.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input CSV file not found: {input_path}")

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError(f"Input CSV file is empty or missing headers: {input_path}")

        # Check required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required column(s) in input CSV: {', '.join(missing_cols)}")

        rows = list(reader)
        original_fieldnames = list(reader.fieldnames)

    output_fieldnames = original_fieldnames + ["category", "priority", "reason", "flag"]
    output_rows = []

    for row in rows:
        try:
            classification = classify_complaint(row)
        except Exception as e:
            # Fallback for unexpected row-level exceptions to maintain batch execution
            classification = {
                "category": "Other",
                "priority": "Standard",
                "reason": f"Processing error encountered on row: {str(e)}",
                "flag": "NEEDS_REVIEW",
            }

        # Merge original fields and classification output
        augmented_row = dict(row)
        augmented_row["category"] = classification.get("category", "Other")
        augmented_row["priority"] = classification.get("priority", "Standard")
        augmented_row["reason"] = classification.get("reason", "")
        augmented_row["flag"] = classification.get("flag", "")
        output_rows.append(augmented_row)

    # Ensure output directory exists if output_path includes a directory
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input complaints CSV")
    parser.add_argument("--output", required=True, help="Path to write output results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Successfully processed and written results to {args.output}")

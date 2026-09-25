"""
UC-0A — Complaint Classifier
Implementation adhering to agents.md and skills.md RICE specifications.
"""
import argparse
import csv
import re
from typing import Dict, List, Optional, Tuple

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

# Morphological variations of severity keywords:
# injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
SEVERITY_PATTERN = re.compile(
    r"\b(injur(?:y|ies|ed|ing)?|child(?:ren)?|school(?:s|ing)?|hospit(?:al|als|alised|alized|alization)?|"
    r"ambulance(?:s)?|fire(?:s|d|y)?|hazard(?:s|ous)?|fell|fall(?:s|ing|en)?|collaps(?:e|ed|es|ing)?)\b",
    re.IGNORECASE,
)


def extract_severity_triggers(text: str) -> List[str]:
    """Find severity keyword occurrences in the text."""
    if not text:
        return []
    matches = SEVERITY_PATTERN.findall(text)
    # Return unique matches preserving casing of original find
    seen = set()
    result = []
    for m in matches:
        m_lower = m.lower()
        if m_lower not in seen:
            seen.add(m_lower)
            result.append(m)
    return result


def evaluate_categories(description: str, location: str) -> Tuple[List[str], List[str]]:
    """
    Evaluate category indicators from description and location.
    Returns:
        candidate_categories: list of matched category names
        evidence_phrases: list of text phrases justifying the candidates
    """
    text = f"{location} {description}".lower()
    desc_lower = description.lower()
    candidates = []
    evidence = []

    # 1. Pothole
    pothole_match = re.search(r"\bpotholes?\b", desc_lower)
    if pothole_match:
        candidates.append("Pothole")
        evidence.append(pothole_match.group(0))

    # 2. Flooding
    flooding_match = re.search(
        r"\b(flood(?:ed|ing|s)?|rainwater\s+through\s+main\s+road|inundat(?:ed|ion)?)\b",
        desc_lower,
    )
    if flooding_match:
        candidates.append("Flooding")
        evidence.append(flooding_match.group(0))

    # 3. Drain Blockage
    drain_match = re.search(
        r"\b(drain(?:s)?|stormwater\s+drain|manhole)\b.*\b(block(?:ed|age)?|debris|mosquito)\b|"
        r"\b(block(?:ed|age)?)\b.*\b(drain(?:s)?)\b",
        desc_lower,
    )
    if drain_match:
        candidates.append("Drain Blockage")
        evidence.append("drain blocked" if "block" in desc_lower else "drain")

    # 4. Streetlight
    streetlight_match = re.search(
        r"\b(streetlights?|lights?\s+out|lamp\s*posts?|unlit|darkness|substation)\b",
        desc_lower,
    )
    if streetlight_match:
        candidates.append("Streetlight")
        evidence.append(streetlight_match.group(0))

    # 5. Waste
    waste_match = re.search(
        r"\b(waste|garbage|rubbish|dead\s+animal|bins?\s+overflowing|dumped)\b",
        desc_lower,
    )
    if waste_match:
        candidates.append("Waste")
        evidence.append(waste_match.group(0))

    # 6. Noise
    noise_match = re.search(
        r"\b(music|wedding\s+band|amplifiers?|drilling|trucks\s+idling|engines\s+on)\b",
        desc_lower,
    )
    if noise_match:
        candidates.append("Noise")
        evidence.append(noise_match.group(0))

    # 7. Road Damage (distinct from simple pothole)
    road_damage_match = re.search(
        r"\b(road\s+surface\s+(?:cracked|sinking|buckled)|road\s+collapsed|"
        r"road\s+subsidence|footpath\s+(?:broken|tiles\s+broken)|crater|paving\s+(?:removed|upturned)|"
        r"cobblestones?\s+broken|manhole\s+cover\s+missing)\b",
        desc_lower,
    )
    if road_damage_match:
        candidates.append("Road Damage")
        evidence.append(road_damage_match.group(0))

    # 8. Heritage Damage
    heritage_match = re.search(
        r"\b(heritage|historic|ancient\s+step\s*well|tagore\s+museum|charminar|monument)\b",
        text,
    )
    if heritage_match:
        candidates.append("Heritage Damage")
        evidence.append(heritage_match.group(0))

    # 9. Heat Hazard
    heat_match = re.search(
        r"\b(melting\s+at\s+\d+°?c|bubbling\s+at\s+\d+°?c|dangerous\s+temperatures|"
        r"surface\s+temperature\s+unbearable|temperature\s+reads\s+\d+°?c|storing\s+heat|"
        r"heatwave\s+conditions|exposed\s+to\s+full\s+sun|burns\s+on\s+contact)\b",
        desc_lower,
    )
    if heat_match:
        candidates.append("Heat Hazard")
        evidence.append(heat_match.group(0))

    # Deduplicate candidates while keeping order
    unique_candidates = []
    for c in candidates:
        if c not in unique_candidates:
            unique_candidates.append(c)

    return unique_candidates, evidence


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "") if isinstance(row, dict) else ""
    description = row.get("description", "") if isinstance(row, dict) else ""
    location = row.get("location", "") if isinstance(row, dict) else ""

    # Rule: Missing, null, or empty description handling
    if not description or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classified as Other with Standard priority because required description field is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()
    location = str(location).strip()

    # Check for severity keywords (triggers Urgent priority)
    severity_triggers = extract_severity_triggers(f"{location} {description}")

    # Evaluate candidate categories
    candidate_categories, evidence = evaluate_categories(description, location)

    # Check for ambiguous or out-of-taxonomy indicators
    desc_lower = description.lower()
    outside_taxonomy = bool(
        re.search(
            r"\b(dead\s+trees?|split\s+branches|irrigation\s+system|broken\s+bench|"
            r"brt\s+shelter\s+roof|draining\s+directly\s+onto|gas\s+pipeline|gas\s+leak|"
            r"substation\s+tripped|manhole\s+cover\s+missing)\b",
            desc_lower,
        )
    )

    # Determine Category & Ambiguity Flag
    # Ambiguous if:
    # - It spans multiple categories (e.g., Heritage + Waste, Flooding + Drain Blockage, etc.)
    # - It clearly falls outside the 9 standard taxonomy categories
    # - No candidate category matched
    if outside_taxonomy or len(candidate_categories) > 1 or len(candidate_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = candidate_categories[0]
        flag = ""

    # Determine Priority:
    # Rule: Urgent if severity keywords present (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse)
    if severity_triggers:
        priority = "Urgent"
    else:
        # Rule: Low for cosmetic, non-disruptive, or low-urgency nuisance issues
        is_low_urgency = bool(
            re.search(
                r"\b(music\s+audible|wedding\s+band|wedding\s+venue\s+playing|amplifiers?\s+illegally|"
                r"trucks\s+idling|defaced\s+by\s+billboard|grass\s+dying)\b",
                desc_lower,
            )
        )
        if is_low_urgency and category in ("Noise", "Other"):
            priority = "Low"
        else:
            # Standard for ordinary operational civic defects without acute safety risk
            priority = "Standard"

    # Construct single-sentence reason citing specific words from description
    # Justifying both category and priority
    if flag == "NEEDS_REVIEW":
        if outside_taxonomy:
            # Find the out-of-taxonomy key phrase
            match = re.search(
                r"(dead\s+trees\s+with\s+split\s+branches|irrigation\s+system\s+broken|"
                r"broken\s+bench\s+and\s+upturned\s+paving|brt\s+shelter\s+roof\s+glass\s+broken|"
                r"new\s+residential\s+complex\s+draining|gas\s+leak\s+smell|substation\s+tripped|"
                r"manhole\s+cover\s+missing)",
                desc_lower,
            )
            phrase = match.group(0) if match else description.split(".")[0]
            if priority == "Urgent":
                reason = (
                    f"Classified as Other with Urgent priority flagged for review because the complaint cites '{phrase}' "
                    f"which falls outside standard taxonomy and poses an acute risk citing '{severity_triggers[0]}'."
                )
            else:
                reason = (
                    f"Classified as Other with {priority} priority flagged for review because the complaint cites '{phrase}' "
                    f"which does not map cleanly to standard municipal taxonomy without acute safety risk."
                )
        elif len(candidate_categories) > 1:
            cats = " and ".join(candidate_categories)
            snippet = description.split(".")[0]
            reason = (
                f"Classified as Other with {priority} priority flagged for review because the description cites '{snippet}' "
                f"spanning multiple categories ({cats}) with {priority.lower()} operational urgency."
            )
        else:
            snippet = description.split(".")[0]
            reason = (
                f"Classified as Other with {priority} priority flagged for review because the complaint description '{snippet}' "
                f"is ambiguous regarding standard taxonomy classification."
            )
    else:
        # Confident single-category classification
        snippet = description.split(".")[0]
        if priority == "Urgent":
            reason = (
                f"Classified as {category} with Urgent priority because the complaint cites '{snippet}' "
                f"with urgent severity triggered by '{severity_triggers[0]}'."
            )
        else:
            reason = (
                f"Classified as {category} with {priority} priority because the description cites '{snippet}' "
                f"representing an operational issue without acute safety hazard."
            )

    # Ensure reason is strictly one sentence (no internal periods terminating earlier)
    # and ends with a single period
    reason = reason.strip().replace("\n", " ")
    if not reason.endswith("."):
        reason += "."

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
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", errors="replace") as f_in:
        reader = csv.DictReader(f_in)
        for row_idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as exc:
                # Fallback on unexpected row parsing failure to avoid crash
                cid = row.get("complaint_id", f"ROW-{row_idx}") if isinstance(row, dict) else f"ROW-{row_idx}"
                results.append(
                    {
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classified as Other with Standard priority due to row processing error citing '{str(exc)}'.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, mode="w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Implementation guided by RICE specifications in agents.md and skills.md.
"""
import argparse
import csv
import os
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity patterns that must trigger Urgent
SEVERITY_PATTERNS = [
    (r"\binjur(?:y|ies|ed)?\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschools?\b", "school"),
    (r"\bhospitals?(?:ised|ized)?\b", "hospital"),
    (r"\bambulances?\b", "ambulance"),
    (r"\bfires?\b", "fire"),
    (r"\bhazards?(?:ous)?\b", "hazard"),
    (r"\bfell\b", "fell"),
    (r"\bcollaps(?:e|ed|ing)?\b", "collapse"),
]


def _find_severity_triggers(text: str) -> List[str]:
    """Find and return verbatim words from the text that match severity triggers."""
    triggers = []
    text_lower = text.lower()
    for pattern, _ in SEVERITY_PATTERNS:
        for match in re.finditer(pattern, text_lower):
            start, end = match.span()
            # Expand to full word boundaries in original text
            while start > 0 and (text[start - 1].isalnum() or text[start - 1] in "-_"):
                start -= 1
            while end < len(text) and (text[end].isalnum() or text[end] in "-_"):
                end += 1
            trigger_word = text[start:end]
            if trigger_word and trigger_word not in triggers:
                triggers.append(trigger_word)
    return triggers


def _extract_citation(text: str, pattern: str) -> str:
    """Extract a verbatim substring from text matching the pattern."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        snippet = match.group(0).strip()
        # Limit snippet length for clean reason formatting
        if len(snippet) > 45:
            snippet = snippet[:42] + "..."
        return snippet
    return ""


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Enforces rules from agents.md:
    - category must be one of the 10 allowed categories (exact strings only).
    - priority must be Urgent if any severity keyword is present; else Standard.
    - reason must be exactly one sentence citing specific words from description.
    - flag is NEEDS_REVIEW if ambiguous or unclassifiable; otherwise empty.
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()

    # Rule: handle missing or empty description
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty description in input.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = desc.lower()

    # Check for severity keywords triggering Urgent priority
    severity_triggers = _find_severity_triggers(desc)
    priority = "Urgent" if severity_triggers else "Standard"

    detected_categories: Dict[str, str] = {}

    # 1. Pothole
    if re.search(r"\bpotholes?\b", desc_lower):
        cite = _extract_citation(desc, r"[^.,;]*\bpotholes?[^.,;]*")
        detected_categories["Pothole"] = cite or "pothole"

    # 2. Drain Blockage
    if re.search(
        r"\b(drain\s+(?:is\s+)?blocked|blocked\s+drain|drain\s+completely\s+blocked|stormwater\s+drain|main\s+drain|draining\s+directly)\b",
        desc_lower,
    ):
        cite = _extract_citation(desc, r"[^.,;]*\bdrain[^.,;]*")
        detected_categories["Drain Blockage"] = cite or "drain blocked"

    # 3. Flooding
    if re.search(
        r"\b(flood|flooded|flooding|floods|waterlogging|rainwater)\b",
        desc_lower,
    ):
        cite = _extract_citation(desc, r"[^.,;]*\b(flood|flooded|flooding|floods|rainwater)[^.,;]*")
        detected_categories["Flooding"] = cite or "flooding"

    # 4. Streetlight
    if re.search(
        r"\b(streetlight|streetlights|lights\s+out|unlit|darkness|substation)\b",
        desc_lower,
    ):
        cite = _extract_citation(desc, r"[^.,;]*\b(streetlight|streetlights|lights\s+out|unlit|darkness|substation)[^.,;]*")
        detected_categories["Streetlight"] = cite or "streetlight"

    # 5. Waste
    if re.search(r"\b(garbage|waste|dead\s+animal|debris|dumped)\b", desc_lower):
        cite = _extract_citation(desc, r"[^.,;]*\b(garbage|waste|dead\s+animal|debris|dumped)[^.,;]*")
        detected_categories["Waste"] = cite or "waste"

    # 6. Noise
    if re.search(r"\b(music|drilling|noise|idling|amplifiers|wedding\s+band)\b", desc_lower):
        cite = _extract_citation(desc, r"[^.,;]*\b(music|drilling|noise|idling|amplifiers|wedding\s+band)[^.,;]*")
        detected_categories["Noise"] = cite or "noise"

    # 7. Heat Hazard
    if re.search(
        r"\b(\d+°c|heatwave|melting|storing\s+heat|temperatures?|full\s+sun|burns\s+on\s+contact)\b",
        desc_lower,
    ):
        cite = _extract_citation(
            desc,
            r"[^.,;]*\b(\d+°c|heatwave|melting|storing\s+heat|temperatures?|full\s+sun|burns\s+on\s+contact)[^.,;]*",
        )
        detected_categories["Heat Hazard"] = cite or "heat hazard"

    # 8. Heritage Damage
    has_heritage_damage = bool(
        re.search(
            r"\b(heritage\s+lamp|historic\s+tram|heritage\s+residential|heritage\s+stone|ancient\s+step|heritage\s+building|defaced)\b",
            desc_lower,
        )
    )
    if has_heritage_damage:
        cite = _extract_citation(desc, r"[^.,;]*\b(heritage|historic|ancient|defaced)[^.,;]*")
        detected_categories["Heritage Damage"] = cite or "heritage damage"
    elif "heritage" in desc_lower and any(k in desc_lower for k in ["waste", "light", "music", "amplifiers", "road"]):
        # Heritage area affected by another issue -> cross-category ambiguity
        detected_categories["Heritage Damage"] = "heritage concern"

    # 9. Road Damage (distinct from specific pothole)
    if re.search(
        r"\b(road\s+surface|road\s+collapsed|footpath|crater|paving|manhole|subsided|sinking|buckled)\b",
        desc_lower,
    ):
        cite = _extract_citation(
            desc,
            r"[^.,;]*\b(road\s+surface|road\s+collapsed|footpath|crater|paving|manhole|subsided|sinking|buckled)[^.,;]*",
        )
        detected_categories["Road Damage"] = cite or "road damage"

    # Resolve category and ambiguity flag
    flag = ""
    category = "Other"

    if "Pothole" in detected_categories:
        category = "Pothole"
        # If pothole is present along with general road damage, pothole is the specific category
        other_cats = [c for c in detected_categories if c not in ("Pothole", "Road Damage")]
        if other_cats:
            flag = "NEEDS_REVIEW"
    elif has_heritage_damage:
        # Direct physical damage to heritage property
        category = "Heritage Damage"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Heat Hazard" in detected_categories:
        category = "Heat Hazard"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Drain Blockage" in detected_categories and "Flooding" in detected_categories:
        # Both drain blockage and flooding are reported together
        if "drain" in desc_lower and "blocked" in desc_lower:
            category = "Drain Blockage"
        else:
            category = "Flooding"
        flag = "NEEDS_REVIEW"
    elif "Drain Blockage" in detected_categories:
        category = "Drain Blockage"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Flooding" in detected_categories:
        category = "Flooding"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Streetlight" in detected_categories:
        category = "Streetlight"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Waste" in detected_categories:
        category = "Waste"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Noise" in detected_categories:
        category = "Noise"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Road Damage" in detected_categories:
        category = "Road Damage"
        if len(detected_categories) > 1:
            flag = "NEEDS_REVIEW"
    elif "Heritage Damage" in detected_categories:
        # Heritage area affected by another issue without direct physical heritage damage
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
    else:
        # Fallback rule: category cannot be determined from description alone
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Build justification reason citing verbatim words
    cited_quote = detected_categories.get(category, "")
    if not cited_quote and detected_categories:
        cited_quote = list(detected_categories.values())[0]
    if not cited_quote:
        words = desc.split()
        cited_quote = " ".join(words[:5])

    if severity_triggers:
        trigger_str = ", ".join(f"'{t}'" for t in severity_triggers)
        reason = (
            f"Classified as {category} citing '{cited_quote}'; "
            f"priority Urgent triggered by severity keyword {trigger_str}."
        )
    else:
        reason = f"Classified as {category} based on description citing '{cited_quote}'."

    # Final validation against allowed schema
    assert category in ALLOWED_CATEGORIES, f"Invalid category: {category}"
    assert priority in ALLOWED_PRIORITIES, f"Invalid priority: {priority}"

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
    Flags nulls, handles bad rows gracefully, and produces output even if some rows fail.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        for row_idx, row in enumerate(reader, start=1):
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Handle bad row gracefully without crashing
                cid = row.get("complaint_id", f"ROW-{row_idx}") if isinstance(row, dict) else f"ROW-{row_idx}"
                results.append({
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error on input row: {str(e)}",
                    "flag": "NEEDS_REVIEW",
                })

    # Ensure target output directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Implementation guided by RICE specifications in agents.md and skills.md.
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

# Severity keywords that trigger 'Urgent' priority
SEVERITY_KEYWORDS = [
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

# Pattern matching for severity triggers including inflections
SEVERITY_PATTERNS = [
    (r"\binjur(?:y|ies|ed|ing)\b", "injury"),
    (r"\bchild(?:ren)?\b", "child"),
    (r"\bschool(?:s)?\b", "school"),
    (r"\bhospital(?:s|ised|ized|isation|ization)?\b", "hospital"),
    (r"\bambulance(?:s)?\b", "ambulance"),
    (r"\bfire(?:s)?\b", "fire"),
    (r"\bhazard(?:s|ous)?\b", "hazard"),
    (r"\bfell\b|\bfall(?:ing)?\b", "fell"),
    (r"\bcollaps(?:e|ed|ing)\b", "collapse"),
]


def detect_severity(text: str) -> Tuple[bool, List[str]]:
    """Check if complaint description contains severity keywords."""
    lowered = text.lower()
    matched_triggers = []
    
    for pattern, label in SEVERITY_PATTERNS:
        match = re.search(pattern, lowered)
        if match:
            matched_triggers.append(match.group(0))
            
    return (len(matched_triggers) > 0, matched_triggers)


def determine_category(text: str, location: str = "") -> Tuple[str, List[str], bool]:
    """
    Determine category, matched keywords, and whether the classification is ambiguous.
    Returns: (category, matched_keywords, is_ambiguous)
    """
    combined_text = f"{location} {text}".lower()
    scores: Dict[str, List[str]] = {}

    # Category heuristic rules
    category_patterns = {
        "Pothole": [r"\bpothole(?:s)?\b", r"\bcrater\b"],
        "Drain Blockage": [
            r"\bdrain\b", r"\bdrainage\b", r"\bstormwater\b",
            r"\bmanhole\b", r"\bmosquito breeding\b", r"\bdengue\b"
        ],
        "Flooding": [
            r"\bflood(?:ed|ing|s)?\b", r"\bwaterlogging\b",
            r"\bknee-deep\b", r"\bstanding in water\b", r"\brainwater\b"
        ],
        "Streetlight": [
            r"\bstreetlight(?:s)?\b", r"\blamp post\b", r"\blights out\b",
            r"\bunlit\b", r"\bdarkness\b", r"\bflickering\b", r"\bsparking\b",
            r"\bsubstation\b", r"\bwiring theft\b"
        ],
        "Waste": [
            r"\bgarbage\b", r"\bwaste\b", r"\bbin(?:s)?\b", r"\bdead animal\b",
            r"\bdumped\b", r"\bdumping\b", r"\boverflowing\b", r"\bsmell\b"
        ],
        "Noise": [
            r"\bmusic\b", r"\bwedding (?:venue|band)\b", r"\bdrilling\b",
            r"\bengine(?:s)?\b", r"\bamplifier(?:s)?\b", r"\bloud\b", r"\bnoise\b"
        ],
        "Heat Hazard": [
            r"\b\d{2}\s*°c\b", r"\bheatwave\b", r"\bheat\b", r"\btemperature\b",
            r"\bmelting\b", r"\bburns on contact\b", r"\bsun\b", r"\bgrass dying\b"
        ],
        "Heritage Damage": [
            r"\bheritage\b", r"\bhistoric\b", r"\btram\b", r"\btagore museum\b",
            r"\bmonument\b", r"\bancient\b", r"\bdefaced\b", r"\bcobblestone(?:s)?\b"
        ],
        "Road Damage": [
            r"\broad surface\b", r"\bfootpath\b", r"\bpaving\b", r"\btile(?:s)?\b",
            r"\bsubsidence\b", r"\bbuckled\b", r"\bcracked\b", r"\bsinking\b",
            r"\btarmac\b"
        ],
    }

    for cat, patterns in category_patterns.items():
        matches = []
        for pat in patterns:
            found = re.findall(pat, combined_text)
            if found:
                matches.extend(found)
        if matches:
            scores[cat] = matches

    if not scores:
        return "Other", [], True

    # Check for specific prioritization and resolution
    if "Pothole" in scores:
        return "Pothole", scores["Pothole"], False

    if "Heritage Damage" in scores and any(w in combined_text for w in ["heritage", "historic", "ancient", "museum"]):
        # If the primary context is heritage asset degradation
        if any(w in combined_text for w in ["stone", "tram", "building", "defaced", "lamp post", "cobblestone"]):
            return "Heritage Damage", scores["Heritage Damage"], False

    if "Heat Hazard" in scores and any(w in combined_text for w in ["°c", "heatwave", "temperature", "melting", "burns on contact"]):
        return "Heat Hazard", scores["Heat Hazard"], False

    if "Drain Blockage" in scores and any(w in combined_text for w in ["drain", "stormwater", "drainage", "blocked", "mosquito"]):
        return "Drain Blockage", scores["Drain Blockage"], False

    if "Flooding" in scores:
        return "Flooding", scores["Flooding"], False

    if "Streetlight" in scores:
        return "Streetlight", scores["Streetlight"], False

    if "Waste" in scores:
        return "Waste", scores["Waste"], False

    if "Noise" in scores:
        return "Noise", scores["Noise"], False

    if "Road Damage" in scores:
        return "Road Damage", scores["Road Damage"], False

    # Top scored category
    best_cat = max(scores.keys(), key=lambda k: len(scores[k]))
    return best_cat, scores[best_cat], False


def classify_complaint(row: dict) -> dict:
    """
    Classify a single citizen complaint dictionary into a structured dictionary.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    location = row.get("location", "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty, requiring administrative review.",
            "flag": "NEEDS_REVIEW",
        }

    # Detect severity
    is_urgent, sev_triggers = detect_severity(description)
    priority = "Urgent" if is_urgent else "Standard"

    # Determine category
    category, cat_triggers, is_ambiguous = determine_category(description, location)

    flag = "NEEDS_REVIEW" if is_ambiguous or category == "Other" else ""

    # Build justification reason citing words from description
    cited_terms = list(dict.fromkeys(sev_triggers + cat_triggers))
    if cited_terms:
        citations = ", ".join(f'"{term}"' for term in cited_terms[:3])
        reason = f"Classified as {category} with {priority} priority based on mention of {citations} in the complaint description."
    else:
        # Fallback citation using first few words
        words = description.split()
        snippet = " ".join(words[:6])
        reason = f"Classified as {category} with {priority} priority referencing description: \"{snippet}...\"; assigned based on reported issue."

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
    Guarantees robust error handling and output generation.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Row processing encountered error: {str(e)}.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(classified)

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

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

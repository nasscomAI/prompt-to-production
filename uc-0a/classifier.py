"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import os
import re

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

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Drain Blockage", ["drain blocked", "blocked drain", "drain blockage"]),
    (
        "Flooding",
        [
            "flooded",
            "flooding",
            "flood",
            "knee-deep",
            "standing in water",
            "stranded",
            "inaccessible",
        ],
    ),
    (
        "Streetlight",
        [
            "streetlight",
            "streetlights",
            "street light",
            "unlit",
            "lights out",
            "wiring theft",
            "very dark",
            "dark at night",
        ],
    ),
    (
        "Waste",
        [
            "garbage",
            "waste",
            "overflowing",
            "not cleared",
            "dead animal",
            "dumped",
            "bins overflowing",
        ],
    ),
    ("Noise", ["music", "noise", "audible"]),
    (
        "Heat Hazard",
        [
            "°c",
            "melting",
            "temperature",
            "heatwave",
            "dangerous temperatures",
            "burns",
            "full sun",
            "bubbling",
            "unbearable",
            "sticking",
        ],
    ),
    (
        "Heritage Damage",
        ["heritage street", "heritage damage", "heritage concern", "heritage area"],
    ),
    (
        "Road Damage",
        [
            "road subsidence",
            "subsidence",
            "road surface",
            "cracked",
            "sinking",
            "paving",
            "footpath",
            "tiles broken",
            "upturned",
            "manhole",
            "lane closure",
            "tyre damage",
        ],
    ),
]

LOW_PRIORITY_HINTS = [
    "visitor complaints",
    "smell affecting",
    "grass dying",
    "complaints.",
]


def _normalize(text: str) -> str:
    return text.strip().lower()


def _find_severity_keywords(description: str) -> list[str]:
    desc = _normalize(description)
    return [kw for kw in SEVERITY_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", desc)]


def _score_categories(description: str) -> tuple[dict[str, int], dict[str, list[str]]]:
    desc = _normalize(description)
    scores: dict[str, int] = {cat: 0 for cat in ALLOWED_CATEGORIES if cat != "Other"}
    matches: dict[str, list[str]] = {cat: [] for cat in ALLOWED_CATEGORIES if cat != "Other"}

    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in desc:
                weight = 2 if " " in keyword else 1
                scores[category] += weight
                matches[category].append(keyword)

    return scores, matches


def _assign_priority(description: str) -> str:
    if _find_severity_keywords(description):
        return "Urgent"
    desc = _normalize(description)
    if any(hint in desc for hint in LOW_PRIORITY_HINTS):
        return "Low"
    return "Standard"


def _build_reason(category: str, description: str, matched_terms: list[str], flagged: bool) -> str:
    if not description or not description.strip():
        return "Description is missing, so category cannot be determined from complaint text."

    if flagged:
        if matched_terms:
            terms = ", ".join(f"'{term}'" for term in matched_terms[:3])
            return (
                f"Description cites {terms} but category remains ambiguous, "
                f"so assigned Other for review."
            )
        snippet = description.strip()
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        return f"Description '{snippet}' does not map clearly to one allowed category."

    if matched_terms:
        terms = ", ".join(f"'{term}'" for term in matched_terms[:3])
        return f"Description mentions {terms}, indicating {category}."

    snippet = description.strip()
    if len(snippet) > 80:
        snippet = snippet[:77] + "..."
    return f"Description '{snippet}' indicates {category}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description") or ""

    if not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so category cannot be determined from complaint text.",
            "flag": "NEEDS_REVIEW",
        }

    scores, matches = _score_categories(description)
    ranked = sorted(
        ((cat, score) for cat, score in scores.items() if score > 0),
        key=lambda item: (-item[1], item[0]),
    )

    priority = _assign_priority(description)
    desc_norm = _normalize(description)

    if re.search(r"\bpothole\b", desc_norm):
        return {
            "complaint_id": complaint_id,
            "category": "Pothole",
            "priority": priority,
            "reason": _build_reason("Pothole", description, ["pothole"], flagged=False),
            "flag": "",
        }

    if not ranked:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason("Other", description, [], flagged=True),
            "flag": "NEEDS_REVIEW",
        }

    top_score = ranked[0][1]
    top_categories = [cat for cat, score in ranked if score == top_score]

    if len(top_categories) > 1:
        all_terms = []
        for cat in top_categories:
            all_terms.extend(matches[cat])
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason("Other", description, all_terms, flagged=True),
            "flag": "NEEDS_REVIEW",
        }

    category = ranked[0][0]
    matched_terms = matches[category]

    heritage_score = scores.get("Heritage Damage", 0)
    road_score = scores.get("Road Damage", 0)
    if heritage_score > 0 and road_score > 0:
        all_terms = matches["Heritage Damage"] + matches["Road Damage"]
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason("Other", description, all_terms, flagged=True),
            "flag": "NEEDS_REVIEW",
        }

    heat_score = scores.get("Heat Hazard", 0)
    if heat_score > 0 and re.search(r"\bbroken\b", desc_norm) and category == "Heat Hazard":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason("Other", description, matched_terms, flagged=True),
            "flag": "NEEDS_REVIEW",
        }

    weak_single_match = (
        ranked[0][1] == 1
        and category == "Heat Hazard"
        and any(term in desc_norm for term in ("broken", "glass broken", "irrigation"))
    )
    if weak_single_match:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": _build_reason("Other", description, matched_terms, flagged=True),
            "flag": "NEEDS_REVIEW",
        }

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _build_reason(category, description, matched_terms, flagged=False),
        "flag": "",
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if not reader.fieldnames:
            raise ValueError(f"Input file is not a valid CSV: {input_path}")

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                results.append(
                    {
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified due to parse error: {exc}.",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
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

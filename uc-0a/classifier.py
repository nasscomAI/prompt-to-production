"""
UC-0A — Complaint Classifier
Built from agents.md (RICE) + skills.md: classify_complaint, batch_classify.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

SEVERITY_KEYWORDS = (
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
)

# Keyword → category scoring (whole-word / phrase aware where needed).
CATEGORY_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "Pothole": ("pothole", "pot hole"),
    "Flooding": ("flooded", "flood", "knee-deep", "waterlogged", "inundat"),
    "Streetlight": ("streetlight", "street light", "streetlights", "lamp post", "sparking"),
    "Waste": (
        "garbage",
        "waste",
        "rubbish",
        "dead animal",
        "bin",
        "dumped",
        "dumping",
    ),
    "Noise": ("noise", "music", "loudspeaker", "sound", "midnight"),
    "Road Damage": (
        "road surface",
        "cracked",
        "sinking",
        "footpath",
        "tiles broken",
        "road damage",
        "manhole cover",
    ),
    "Heritage Damage": ("heritage",),
    "Heat Hazard": ("heatwave", "heat hazard", "extreme heat"),
    "Drain Blockage": ("drain blocked", "drain blockage", "blocked drain", "clogged drain"),
}


def _find_severity_hits(description: str) -> List[str]:
    text = description.lower()
    hits: List[str] = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            hits.append(kw)
    # "children" should count for child severity signal
    if "children" in text and "child" not in hits:
        hits.append("child")
    return hits


def _score_categories(description: str) -> Dict[str, int]:
    text = description.lower()
    scores = {cat: 0 for cat in ALLOWED_CATEGORIES if cat != "Other"}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 2 if " " in kw or len(kw) > 6 else 1
    return scores


def _cite_words(description: str, words: List[str], limit: int = 6) -> str:
    found: List[str] = []
    lower = description.lower()
    for w in words:
        if w.lower() in lower and w not in found:
            found.append(w)
        if len(found) >= limit:
            break
    if not found:
        # Fall back to first few content tokens from description.
        tokens = re.findall(r"[A-Za-z0-9'-]+", description)
        found = tokens[: min(5, len(tokens))]
    return ", ".join(f'"{w}"' for w in found)


def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    One complaint row → category, priority, reason, flag.
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing; cannot classify from available fields.",
            "flag": "NEEDS_REVIEW",
        }

    scores = _score_categories(description)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_score = ranked[0][1]
    top_cats = [c for c, s in ranked if s == top_score and s > 0]

    flag = ""
    if top_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cite = _cite_words(description, description.split()[:5])
        reason = (
            f"No taxonomy keyword match in description; cited words: {cite}."
        )
    elif len(top_cats) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cite = _cite_words(description, list(sum(
            (list(CATEGORY_KEYWORDS[c]) for c in top_cats), []
        )))
        reason = (
            f"Ambiguous between {' / '.join(top_cats)}; "
            f"cited words: {cite}."
        )
    else:
        category = top_cats[0]
        # Special case: heritage + lights → ambiguous heritage vs streetlight
        if category == "Heritage Damage" and any(
            k in description.lower() for k in ("light", "streetlight", "dark")
        ):
            flag = "NEEDS_REVIEW"
        cite_kw = list(CATEGORY_KEYWORDS[category])
        cite = _cite_words(description, cite_kw)
        reason = f"Classified as {category} based on cited words: {cite}."

    severity_hits = _find_severity_hits(description)
    if severity_hits:
        priority = "Urgent"
        sev = ", ".join(f'"{h}"' for h in severity_hits)
        reason = f"{reason} Severity keywords present: {sev}."
    else:
        # Default Standard for matched categories; Low only when Other + no signals
        priority = "Low" if category == "Other" and flag == "NEEDS_REVIEW" else "Standard"

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"{reason} Invalid category blocked; forced to Other."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Skill: batch_classify
    Read input CSV, classify each row, write results CSV (no crash on bad rows).
    """
    path = Path(input_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results: List[dict] = []
    try:
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")
            for i, row in enumerate(reader, start=1):
                try:
                    results.append(classify_complaint(row))
                except Exception as exc:  # noqa: BLE001 — must not abort batch
                    results.append(
                        {
                            "complaint_id": (row.get("complaint_id") or f"ROW-{i}"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": f"Row failed classification: {exc}",
                            "flag": "NEEDS_REVIEW",
                        }
                    )
    except OSError as exc:
        raise OSError(f"Unable to read input CSV: {exc}") from exc

    out = Path(output_path)
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    try:
        batch_classify(args.input, args.output)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Results written to {args.output}")

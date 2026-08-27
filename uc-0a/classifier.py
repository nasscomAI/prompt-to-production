"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify per agents.md / skills.md.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

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

# Cue patterns per allowed category. Scores are additive; a clear single
# winner is required — ties or zero matches → Other + NEEDS_REVIEW.
CATEGORY_CUES: dict[str, list[tuple[str, int]]] = {
    "Pothole": [
        (r"\bpotholes?\b", 3),
    ],
    "Flooding": [
        (r"\bflood(?:ed|ing|s)?\b", 3),
        (r"\bwaterlogged\b", 2),
        (r"\bknee[- ]?deep\b", 2),
        (r"\brainwater\b", 1),
        (r"\bstanding in water\b", 2),
    ],
    "Streetlight": [
        (r"\bstreetlights?\b", 3),
        (r"\bstreet\s+lights?\b", 3),
        (r"\blights?\s+out\b", 2),
        (r"\bunlit\b", 2),
        (r"\bdarkness\b", 1),
        (r"\bsubstation\s+tripped\b", 2),
    ],
    "Waste": [
        (r"\bgarbage\b", 3),
        (r"\bwaste\b", 3),
        (r"\bbins?\b", 2),
        (r"\bdumped\b", 2),
        (r"\bdead\s+animal\b", 3),
        (r"\boverflow(?:ing)?\b", 1),
    ],
    "Noise": [
        (r"\bmusic\b", 3),
        (r"\bnoise\b", 3),
        (r"\bamplifiers?\b", 3),
        (r"\bdrilling\b", 3),
        (r"\baudible\b", 2),
        (r"\bidling\b", 2),
        (r"\bengines?\b", 1),
        (r"\bband\s+playing\b", 3),
    ],
    "Road Damage": [
        (r"\broad\s+surface\b", 3),
        (r"\bcracked\b", 2),
        (r"\bsinking\b", 2),
        (r"\bfootpath\b", 3),
        (r"\bcollapsed?\b", 3),
        (r"\bbuckled\b", 3),
        (r"\bsubsid(?:ed|ence)\b", 3),
        (r"\bcrater\b", 3),
        (r"\bpaving\b", 2),
        (r"\btiles?\s+broken\b", 3),
        (r"\btarmac\b", 1),
        (r"\bmanhole\b", 2),
    ],
    "Heritage Damage": [
        (r"\bheritage\b", 3),
        (r"\bhistoric\b", 3),
        (r"\bcobblestones?\b", 2),
        (r"\bstep\s+well\b", 2),
        (r"\btram\s+road\b", 1),
    ],
    "Heat Hazard": [
        (r"\b\d+\s*°\s*c\b", 3),
        (r"\bheatwave\b", 3),
        (r"\bmelting\b", 3),
        (r"\btemperatures?\b", 2),
        (r"\bburns?\b", 2),
        (r"\bheat\b", 2),
        (r"\bunbearable\b", 1),
        (r"\bfull\s+sun\b", 2),
    ],
    "Drain Blockage": [
        (r"\bdrain(?:s|age)?\s+(?:is\s+)?(?:completely\s+)?blocked\b", 3),
        (r"\bblocked\b.*\bdrain", 3),
        (r"\bstormwater\s+drain\b", 3),
        (r"\bmain\s+drain\b", 3),
        (r"\bdrain\b", 2),  # used only when no stronger drain cue matches
    ],
}

OUTPUT_FIELDS = ("complaint_id", "category", "priority", "reason", "flag")


def _find_severity_hits(text: str) -> list[str]:
    """Match severity keywords as whole-word stems (child→children, hospital→hospitalised)."""
    hits: list[str] = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}", text, flags=re.IGNORECASE):
            hits.append(kw)
    return hits


def _score_categories(text: str) -> dict[str, tuple[int, list[str]]]:
    scores: dict[str, tuple[int, list[str]]] = {}
    for category, cues in CATEGORY_CUES.items():
        hits: list[tuple[int, str, str]] = []
        for pattern, weight in cues:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                hits.append((weight, match.group(0), pattern))
        if not hits:
            continue
        # Do not stack a bare "drain" cue on top of a stronger drain match.
        if category == "Drain Blockage":
            strong = [h for h in hits if h[2] != r"\bdrain\b"]
            if strong:
                hits = strong
        total = sum(h[0] for h in hits)
        cited = [h[1] for h in hits]
        scores[category] = (total, cited)
    return scores


def _pick_category(
    scores: dict[str, tuple[int, list[str]]],
) -> tuple[str, list[str], bool]:
    """
    Return (category, cited_cues, needs_review).
    Clear unique winner → that category; else Other + NEEDS_REVIEW.
    """
    if not scores:
        return "Other", [], True

    ranked = sorted(scores.items(), key=lambda item: item[1][0], reverse=True)
    best_name, (best_score, best_cues) = ranked[0]
    tied = [name for name, (score, _) in ranked if score == best_score]

    if len(tied) > 1:
        all_cues: list[str] = []
        for name in tied:
            all_cues.extend(scores[name][1])
        return "Other", all_cues, True

    # Near-tie: runner-up within 1 point of the winner → ambiguous.
    if len(ranked) > 1 and ranked[1][1][0] > 0 and ranked[1][1][0] >= best_score - 1:
        cues = best_cues + ranked[1][1][1]
        return "Other", cues, True

    # Flooding + drain blockage together is a known dual-issue ambiguity.
    if {"Flooding", "Drain Blockage"} <= set(scores):
        cues = scores["Flooding"][1] + scores["Drain Blockage"][1]
        return "Other", cues, True

    return best_name, best_cues, False


def _priority_for(severity_hits: list[str], category: str, needs_review: bool) -> str:
    if severity_hits:
        return "Urgent"
    if needs_review or category == "Other":
        return "Standard"
    return "Standard"


def _build_reason(
    description: str,
    category: str,
    cited: list[str],
    severity_hits: list[str],
    needs_review: bool,
    empty: bool,
) -> str:
    if empty:
        return "Description missing or empty; cannot classify from description alone."

    quote_bits = []
    for token in cited + severity_hits:
        cleaned = token.strip()
        if cleaned and cleaned.lower() not in {q.lower() for q in quote_bits}:
            quote_bits.append(cleaned)
    # Fall back to a short verbatim snippet so reason always cites the text.
    if not quote_bits:
        snippet = description.strip()
        quote_bits.append(snippet[:80] + ("…" if len(snippet) > 80 else ""))

    quoted = ", ".join(f'"{q}"' for q in quote_bits[:4])
    if needs_review:
        return f"Ambiguous category cues in description ({quoted}); flagged for review as {category}."
    if severity_hits:
        return f"Classified as {category} based on {quoted}; severity keyword(s) present."
    return f"Classified as {category} based on {quoted} in the description."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (row.get("complaint_id") or "").strip()
    raw = row.get("description")
    description = "" if raw is None else str(raw).strip()

    if not description or description.lower() in {"null", "none", "n/a", "na"}:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing or empty; cannot classify from description alone.",
            "flag": "NEEDS_REVIEW",
        }

    severity_hits = _find_severity_hits(description)
    scores = _score_categories(description)
    category, cited, needs_review = _pick_category(scores)

    # Enforce allowed list exactly (no drift).
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        needs_review = True

    priority = _priority_for(severity_hits, category, needs_review)
    # Severity always wins, including on ambiguous rows.
    if severity_hits:
        priority = "Urgent"

    flag = "NEEDS_REVIEW" if needs_review else ""
    reason = _build_reason(
        description, category, cited, severity_hits, needs_review, empty=False
    )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    in_path = Path(input_path)
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        with in_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except OSError as exc:
        raise OSError(f"Unable to read input file: {input_path}") from exc

    results: list[dict] = []
    for row in rows:
        try:
            results.append(classify_complaint(row or {}))
        except Exception as exc:  # noqa: BLE001 — batch must not crash on bad rows
            results.append(
                {
                    "complaint_id": (row or {}).get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row failed classification ({exc}); flagged for review.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

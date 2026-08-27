"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
from pathlib import Path

# README: severity keywords → Urgent
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

# (category, keywords that support that category) — order matters for tie-breaking preference
_CATEGORY_KEYWORDS = [
    ("Heritage Damage", ("heritage",)),
    ("Drain Blockage", ("drain block", "blocked drain", "clogged drain", "drainage block")),
    ("Heat Hazard", ("heat stroke", "heatstroke", "extreme heat", "heat hazard")),
    ("Pothole", ("pothole", "crater")),
    ("Flooding", ("flood", "flooded", "flooding", "knee-deep", "underpass")),
    ("Streetlight", ("streetlight", "street light", "street lights", "lights out", "flickering")),
    ("Waste", ("garbage", "bins", "bulk waste", "dumped", "dead animal", "overflowing")),
    ("Noise", ("music", " noise", "midnight", "loud")),  # space before noise avoids matching 'annoying' poorly
    ("Road Damage", ("cracked", "sinking", "manhole", "footpath", "tiles broken", "upturned")),
]


def _urgent(description: str) -> bool:
    lower = description.lower()
    return any(kw in lower for kw in SEVERITY_KEYWORDS)


def _score_categories(description: str) -> dict[str, int]:
    lower = description.lower()
    scores: dict[str, int] = {cat: 0 for cat, _ in _CATEGORY_KEYWORDS}
    scores["Other"] = 0
    for cat, keywords in _CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw.strip() in lower:
                scores[cat] += 1
    return scores


def _pick_category(description: str) -> tuple[str, bool]:
    """Returns (category, needs_review)."""
    scores = _score_categories(description)
    ranked = sorted(
        ((c, s) for c, s in scores.items() if c != "Other"),
        key=lambda x: (-x[1], x[0]),
    )
    best_score = ranked[0][1] if ranked else 0
    if best_score == 0:
        return "Other", True
    top = [c for c, s in ranked if s == best_score and s > 0]
    if len(top) > 1:
        return "Other", True
    return top[0], False


def _reason_snippet(description: str, category: str) -> str:
    """One sentence citing words from the description."""
    lower = description.lower()
    hits: list[str] = []
    for _, keywords in _CATEGORY_KEYWORDS:
        for kw in keywords:
            k = kw.strip()
            if k and k in lower:
                # recover original casing from description
                m = re.search(re.escape(k), description, re.IGNORECASE)
                if m:
                    hits.append(m.group(0))
    if not hits:
        words = description.split()[:8]
        phrase = " ".join(words)
        if len(description) > len(phrase):
            phrase += "…"
        return f'The complaint states: "{phrase}"'
    quoted = ", ".join(f"'{h}'" for h in hits[:3])
    return f"The description uses {quoted}, which supports {category}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    cid = (row.get("complaint_id") or "").strip()
    desc = (row.get("description") or "").strip()

    if not desc:
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description text was provided in the row.",
            "flag": "NEEDS_REVIEW",
        }

    category, ambiguous = _pick_category(desc)
    if ambiguous and category == "Other":
        flag = "NEEDS_REVIEW"
    elif ambiguous:
        flag = "NEEDS_REVIEW"
        category = "Other"
    else:
        flag = ""

    priority = "Urgent" if _urgent(desc) else "Standard"
    reason = _reason_snippet(desc, category)

    return {
        "complaint_id": cid,
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
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows_out: list[dict] = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows_out.append(classify_complaint(row))
            except Exception as e:
                rows_out.append(
                    {
                        "complaint_id": (row or {}).get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Classifier error on row: {e!s}",
                        "flag": "NEEDS_REVIEW",
                    }
                )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

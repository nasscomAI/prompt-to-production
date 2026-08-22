"""
UC-0A — Complaint Classifier
Implements agents.md + skills.md: classify_complaint and batch_classify.
Enforcement rules are coded directly — no external AI calls required.
"""
import argparse
import csv
import sys

# ── Schema constants (from agents.md / UC-0A README) ───────────────────────

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
}

URGENT_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# Keyword → category mapping (first match wins; order matters)
CATEGORY_RULES = [
    ({"pothole"},                                         "Pothole"),
    ({"flood", "flooded", "flooding", "waterlogged"},     "Flooding"),
    ({"streetlight", "street light", "lamp", "lighting"}, "Streetlight"),
    ({"garbage", "waste", "litter", "rubbish", "dump",
      "bins", "animal", "dead animal"},                   "Waste"),
    ({"noise", "music", "sound", "loud"},                 "Noise"),
    ({"road", "cracked", "sinking", "pothole", "manhole",
      "footpath", "pavement", "tiles", "surface"},        "Road Damage"),
    ({"heritage", "historic", "listed", "old city"},      "Heritage Damage"),
    ({"heat", "temperature", "hot"},                      "Heat Hazard"),
    ({"drain", "blocked drain", "blockage", "clogged"},   "Drain Blockage"),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """
    Return (category, needs_review).
    needs_review is True when the match is uncertain.
    """
    desc_lower = description.lower()

    # Heritage check — must be explicit
    if any(kw in desc_lower for kw in {"heritage", "historic", "listed"}):
        return "Heritage Damage", False

    # Drain Blockage — only when no primary flooding language
    if ("drain" in desc_lower or "blockage" in desc_lower or "clogged" in desc_lower):
        if not any(kw in desc_lower for kw in {"flood", "flooded", "flooding", "waterlogged"}):
            return "Drain Blockage", False

    # Walk through ordered rules
    for keywords, category in CATEGORY_RULES:
        if any(kw in desc_lower for kw in keywords):
            return category, False

    return "Other", True


def _detect_priority(description: str) -> str:
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in URGENT_KEYWORDS):
        return "Urgent"
    # Heuristic: long-standing issues → Standard, minor → Low
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """One sentence citing words from the description."""
    # Find the first urgent keyword present, if any
    desc_lower = description.lower()
    triggered = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if triggered and priority == "Urgent":
        return (
            f"Classified as {category} and marked Urgent because the description "
            f"contains '{triggered[0]}': \"{description[:80].rstrip()}\"."
        )
    # Truncate description for the reason sentence
    snippet = description[:80].rstrip()
    if len(description) > 80:
        snippet += "…"
    return f"Classified as {category} based on description: \"{snippet}\"."


# ── Skill 1: classify_complaint ─────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input : dict with at least keys 'complaint_id' and 'description'.
    Output: dict with keys complaint_id, category, priority, reason, flag.

    Never raises — returns NEEDS_REVIEW on bad input (skill contract).
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # Guard: empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category":     "Other",
            "priority":     "Low",
            "reason":       "Description insufficient to classify.",
            "flag":         "NEEDS_REVIEW",
        }

    category, needs_review = _detect_category(description)
    priority = _detect_priority(description)
    reason   = _build_reason(description, category, priority)
    flag     = "NEEDS_REVIEW" if needs_review else ""

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


# ── Skill 2: batch_classify ─────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Raises FileNotFoundError / ValueError on bad input before producing output.
    On per-row failures, logs a warning and writes an ERROR row — never crashes.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as exc:
        raise ValueError(f"Could not parse input CSV '{input_path}': {exc}") from exc

    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    for row in rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:
            cid = row.get("complaint_id", "UNKNOWN")
            print(f"WARNING: Row {cid} failed classification: {exc}", file=sys.stderr)
            result = {
                "complaint_id": cid,
                "category":     "ERROR",
                "priority":     "",
                "reason":       "",
                "flag":         "NEEDS_REVIEW",
            }
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

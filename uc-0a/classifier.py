"""
UC-0A — Complaint Classifier

Deterministic, rule-based triage of civic complaints. Enforces the contract in
agents.md / skills.md: an exact category taxonomy, severity-driven Urgent
priority, a cited one-sentence reason, and a NEEDS_REVIEW flag on ambiguity.
No runtime LLM — every decision is a verifiable string check.
"""
import argparse
import csv
import os
import re

# Exact category taxonomy — no variations, plurals, or invented sub-categories.
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]
PRIORITIES = ["Urgent", "Standard", "Low"]

# Any of these, matched as a substring of a word (so hospitalised, collapsed,
# children all count), forces Urgent regardless of category.
SEVERITY_TERMS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

_WORD_RE = re.compile(r"[A-Za-z\u00b00-9]+")


def _tokens(text: str) -> list:
    return _WORD_RE.findall(text)


def _actual_word(tokens: list, needle: str) -> str:
    """Return the real description token containing needle, so the reason cites
    a word that actually appears in the row."""
    for word in tokens:
        if needle in word.lower():
            return word
    return needle


def _first_present(text_lower: str, tokens: list, needles: list):
    for needle in needles:
        if needle in text_lower:
            return _actual_word(tokens, needle)
    return None


def _detect_category(description: str):
    """Return (category, [evidence_words]). Order encodes precedence for
    overlapping wording (e.g. waste/noise before heritage context)."""
    t = description.lower()
    toks = _tokens(description)

    # 1. Flooding — actual water on the ground (not merely "flooding risk").
    word = _first_present(t, toks, ["flooded", "floods", "waterlogged", "submerged"])
    if word:
        return "Flooding", [word]

    # 2. Drain Blockage — a drain/sewer that is blocked.
    if ("drain" in t or "sewer" in t) and any(b in t for b in ["block", "clogged", "choked"]):
        drain_w = _actual_word(toks, "drain") if "drain" in t else _actual_word(toks, "sewer")
        block_w = _first_present(t, toks, ["blocked", "block", "clogged", "choked"])
        return "Drain Blockage", [drain_w, block_w]

    # 3. Heat Hazard.
    word = _first_present(
        t, toks,
        ["heatwave", "melting", "melt", "temperature", "burns", "burn", "overheat", "heat", "\u00b0c"],
    )
    if word or "full sun" in t:
        return "Heat Hazard", [word or "sun"]

    # 4. Waste.
    word = _first_present(t, toks, ["garbage", "waste", "dumped", "dumping", "trash", "litter", "refuse"])
    if not word and "dead animal" in t:
        word = _actual_word(toks, "animal")
    if word:
        return "Waste", [word]

    # 5. Noise.
    word = _first_present(t, toks, ["music", "band", "drilling", "amplifier", "loud", "noise", "idling", "honking"])
    if word:
        return "Noise", [word]

    # 6. Pothole.
    if "pothole" in t:
        return "Pothole", [_actual_word(toks, "pothole")]

    # 7. Heritage Damage — a heritage/historic structure that is damaged.
    if "heritage" in t or "historic" in t:
        dmg = _first_present(
            t, toks,
            ["knocked", "broken", "defaced", "damaged", "restored", "replaced", "removed", "cobbleston"],
        )
        if dmg:
            heri_w = _actual_word(toks, "heritage") if "heritage" in t else _actual_word(toks, "historic")
            return "Heritage Damage", [heri_w, dmg]

    # 8. Streetlight.
    word = _first_present(t, toks, ["streetlight", "unlit", "flickering", "substation", "darkness", "dark"])
    if not word and "lights out" in t:
        word = _actual_word(toks, "lights")
    if not word and "lamp post" in t:
        word = _actual_word(toks, "lamp")
    if word:
        return "Streetlight", [word]

    # 9. Road Damage.
    word = _first_present(
        t, toks,
        ["crack", "sinking", "subsid", "buckled", "crater", "collapse", "manhole", "paving", "footpath", "tiles", "cobbleston"],
    )
    if not word and "road surface" in t:
        word = _actual_word(toks, "road")
    if word:
        return "Road Damage", [word]

    return "Other", []


def _severity_word(description: str):
    t = description.lower()
    toks = _tokens(description)
    for term in SEVERITY_TERMS:
        if term in t:
            return _actual_word(toks, term)
    return None


def _build_reason(description: str, category: str, evidence: list, severity_word) -> str:
    if category != "Other":
        cited = "' and '".join(evidence)
        base = f"Classified as {category} because the description mentions '{cited}'"
    else:
        toks = _tokens(description)
        first = toks[0] if toks else description.strip()
        base = f"No allowed category clearly matched wording such as '{first}', so it was flagged for review"
    if severity_word:
        return f"{base}, and marked Urgent due to '{severity_word}'."
    return f"{base}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        row = {}
    complaint_id = str(row.get("complaint_id") or "").strip()
    description = row.get("description")

    if not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description was missing or empty, so it could not be classified and was flagged for review.",
            "flag": "NEEDS_REVIEW",
        }

    category, evidence = _detect_category(description)
    severity_word = _severity_word(description)

    # Urgent on any severity term; otherwise Standard for actionable text.
    # Low is reserved for empty/unreadable rows (handled above).
    priority = "Urgent" if severity_word else "Standard"
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": _build_reason(description, category, evidence, severity_word),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never aborts on a single bad row; always produces output when input is readable.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    total = failed = needs_review = 0

    with open(input_path, newline="", encoding="utf-8") as fin, \
            open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            total += 1
            try:
                result = classify_complaint(row)
            except Exception as exc:
                failed += 1
                result = {
                    "complaint_id": str((row or {}).get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row could not be processed ({type(exc).__name__}), so it was flagged for review.",
                    "flag": "NEEDS_REVIEW",
                }
            if result["flag"] == "NEEDS_REVIEW":
                needs_review += 1
            writer.writerow(result)

    print(f"Classified {total} row(s) -> {output_path} "
          f"({needs_review} flagged NEEDS_REVIEW, {failed} row error(s)).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)

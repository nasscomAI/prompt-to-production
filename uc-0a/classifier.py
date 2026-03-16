"""
UC-0A — Complaint Classifier
Built following the RICE rules in agents.md and the schema defined in README.md.
"""
import argparse
import csv

# ── Taxonomy (exact strings only, per README) ─────────────────────────────────
CATEGORIES = [
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

# Keyword -> category mapping (checked in order; first match wins for single)
CATEGORY_KEYWORDS: list[tuple[list[str], str]] = [
    (["pothole", "pot hole", "pot-hole", "crater", "hole in road", "road hole"], "Pothole"),
    (["flood", "waterlog", "water log", "inundated", "submerged", "overflow",
      "water stagnation", "stagnant water"], "Flooding"),
    (["streetlight", "street light", "lamp post", "lamp-post", "light out",
      "no light", "dark street", "broken light", "light not working"], "Streetlight"),
    (["garbage", "waste", "trash", "litter", "rubbish", "dump", "debris", "refuse"], "Waste"),
    (["noise", "loud", "sound", "music", "horn", "blaring", "honking",
      "disturbance", "nuisance"], "Noise"),
    (["road damage", "road crack", "cracked road", "broken road", "damaged road",
      "road broken", "road surface", "tarmac"], "Road Damage"),
    (["heritage", "monument", "historical", "ancient", "temple", "fort",
      "statue", "structure damage"], "Heritage Damage"),
    (["heat", "hot", "scorching", "temperature", "heatwave", "heat wave",
      "overheating"], "Heat Hazard"),
    (["drain", "drainage", "sewer", "blocked drain", "clog", "choke",
      "stormwater", "gutter"], "Drain Blockage"),
]

# Severity keywords that trigger Urgent priority (per README)
URGENCY_KEYWORDS = [
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "fallen", "collapse", "collapsed",
]


def _find_category(description: str) -> tuple[str, bool]:
    """
    Return (category, is_ambiguous).
    is_ambiguous=True when no keyword matches, or multiple categories match.
    """
    text = description.lower()
    matches: list[str] = []
    for keywords, category in CATEGORY_KEYWORDS:
        if any(kw in text for kw in keywords):
            matches.append(category)

    if len(matches) == 1:
        return matches[0], False
    if len(matches) > 1:
        # Multiple categories matched -> keep first but flag as ambiguous
        return matches[0], True
    return "Other", True  # No match -> fallback + flag


def _find_priority(description: str) -> str:
    """Return 'Urgent' if any severity keyword is present, else 'Standard'."""
    text = description.lower()
    if any(kw in text for kw in URGENCY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """
    Build a one-sentence reason citing specific words from the description,
    as required by agents.md enforcement rules.
    """
    stop = {"a", "an", "the", "is", "in", "on", "at", "of", "and", "or",
            "to", "for", "with", "has", "was", "are", "i", "it", "this"}
    words = description.split()
    cited = [w.strip(".,!?;:\"'") for w in words
             if w.lower().strip(".,!?;:\"'") not in stop][:3]
    cited_str = ", ".join(f'"{w}"' for w in cited) if cited else f'"{description[:40]}"'
    urgency_note = " (Urgent: severity keyword detected)" if priority == "Urgent" else ""
    return f"Description mentions {cited_str}; classified as {category}{urgency_note}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Expected input keys : complaint_id, description
    Output keys         : complaint_id, category, priority, reason, flag

    RICE enforcement (from agents.md):
    - Role   : municipal complaint classifier
    - Intent : output category + priority strictly from the allowed schema
    - Context: use ONLY the description field — no external knowledge
    - Enforce:
        * category must be exactly one of the CATEGORIES list
        * priority is Urgent when severity keywords present, else Standard
        * reason must cite specific words from the description
        * flag=NEEDS_REVIEW when category is genuinely ambiguous
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description") or "").strip()

    # Guard: missing / empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _find_category(description)
    priority = _find_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

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

    Resilience rules:
    - Flags null/empty descriptions with NEEDS_REVIEW (does not crash)
    - Catches unexpected errors per row; logs them; continues processing
    - Always produces an output file, even when some rows fail
    """
    output_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    results: list[dict] = []

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        for line_no, row in enumerate(reader, start=2):  # row 1 = header
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001
                complaint_id = row.get("complaint_id", f"row_{line_no}")
                result = {
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
                print(f"[WARN] Row {line_no} (id={complaint_id}) failed: {exc}")
            results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r.get("flag") == "NEEDS_REVIEW")
    urgent = sum(1 for r in results if r.get("priority") == "Urgent")
    print(f"Classified {len(results)} rows — {urgent} Urgent, {flagged} flagged NEEDS_REVIEW.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

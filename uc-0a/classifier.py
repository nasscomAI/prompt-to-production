"""
UC-0A — Complaint Classifier
Implements the rules in agents.md / skills.md.

Classification only: uses the complaint description text and complaint_id,
never the city name or any external knowledge.
"""
import argparse
import csv
import re

CATEGORIES = [
    ("Drain Blockage", [
        "drain", "drains", "drainage", "sewer", "sewage", "gutter", "gutters",
        "manhole", "manholes", "clog", "clogged", "choke", "choked", "choking",
        "drain blocked", "blocked drain", "not draining", "drainage block",
    ]),
    ("Flooding", [
        "flood", "floods", "flooding", "flooded", "waterlogged", "waterlogging",
        "water logging", "rainwater", "rain water", "submerged", "inundation",
        "water accumulation",
    ]),
    ("Pothole", [
        "pothole", "potholes", "crater", "craters",
    ]),
    ("Heritage Damage", [
        "heritage", "monument", "monuments", "historical", "fort", "forts",
        "palace", "ancient", "tomb", "statue",
    ]),
    ("Road Damage", [
        "broken road", "cracked road", "damaged road", "road damage",
        "road surface", "uneven road", "rough road", "dug up", "digging",
    ]),
    ("Streetlight", [
        "streetlight", "streetlights", "street light", "street lights",
        "lamp", "lamps", "lamppost", "lampposts", "lamp post", "lantern",
        "lanterns", "light not", "lights not", "light pole", "lighting",
    ]),
    ("Heat Hazard", [
        "heat", "hot", "hotter", "sun", "sunlight", "heatwave", "heat wave",
        "temperature", "scorching", "sweltering",
    ]),
    ("Waste", [
        "garbage", "waste", "wastes", "trash", "litter", "rubbish", "dumping",
        "dump", "dumped", "debris", "overflowing bin", "garbage bin",
        "waste pile", "waste heap",
    ]),
    ("Noise", [
        "noise", "noises", "noisy", "loud", "louder", "honk", "honking",
        "cacophony", "loudspeaker", "noise pollution", "sound pollution",
    ]),
]

SEVERITY_KEYWORDS = [
    "injury", "injuries", "child", "children", "school", "schools",
    "hospital", "hospitals", "ambulance", "fire", "hazard", "hazards",
    "fell", "collapse", "collapsed", "collapsing",
]

LOW_PHRASES = [
    "no action", "no need", "just informing", "just to inform",
    "informational", "no issue", "no problem", "for information",
]


def _find_match(text: str, keyword: str):
    """Return the keyword as it appears in text (original case), or None."""
    low_text = text.lower()
    low_kw = keyword.lower()
    if " " in low_kw:
        idx = low_text.find(low_kw)
        return text[idx:idx + len(low_kw)] if idx != -1 else None
    m = re.search(r"\b" + re.escape(low_kw) + r"\b", low_text)
    return text[m.start():m.end()] if m else None


def _severity_priority(description: str) -> str:
    if any(_find_match(description, kw) for kw in SEVERITY_KEYWORDS):
        return "Urgent"
    if any(phrase in description.lower() for phrase in LOW_PHRASES):
        return "Low"
    return "Standard"


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id") or ""
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or empty; flagged for review.",
            "flag": "NEEDS_REVIEW",
        }

    category, snippet = "Other", None
    for cat, keywords in CATEGORIES:
        for kw in keywords:
            match = _find_match(description, kw)
            if match:
                category, snippet = cat, match
                break
        if snippet is not None:
            break

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        excerpt = description if len(description) <= 60 else description[:60] + "..."
        reason = (
            f"No supported category matches the description "
            f"('{excerpt}'), so it is classified as Other for review."
        )
    else:
        reason = (
            f"The description mentions '{snippet}', which indicates "
            f"the {category} category."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": _severity_priority(description),
        "reason": reason,
        "flag": flag,
    }


def _pick_column(fieldnames, candidates, rows):
    """Pick the field that best matches candidates, else the longest-text field."""
    for name in fieldnames:
        if name.strip().lower() in candidates:
            return name
    if rows:
        return max(
            fieldnames,
            key=lambda f: sum(len((r.get(f) or "")) for r in rows) / len(rows),
        )
    return fieldnames[0] if fieldnames else None


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, produces output even if some rows fail.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    desc_col = _pick_column(
        fieldnames,
        {"description", "complaint_description", "complaint", "issue",
         "details", "text", "problem", "what happened", "incident"},
        rows,
    )
    id_col = _pick_column(
        fieldnames,
        {"complaint_id", "id", "ticket", "ticket_id", "case_id", "reference"},
        rows,
    )

    results = []
    for row in rows:
        try:
            clean = {
                "complaint_id": row.get(id_col) if id_col else "",
                "description": row.get(desc_col) if desc_col else "",
            }
            results.append(classify_complaint(clean))
        except Exception:
            results.append({
                "complaint_id": row.get(id_col, "") if id_col else "",
                "category": "Other",
                "priority": "Standard",
                "reason": "Error during classification; flagged for review.",
                "flag": "NEEDS_REVIEW",
            })

    out_fields = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Implements the agents.md enforcement rules deterministically:
- category is one of 10 exact strings, never a variation or sub-category
- priority is Urgent on any severity keyword, otherwise imminent-risk, else Standard, else Low
- every row gets a one-sentence reason citing specific words from the description
- ambiguous or empty descriptions become Other + NEEDS_REVIEW, never a guess
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "injured", "injuries", "child", "children", "school", "schools",
    "hospital", "hospitals", "hospitalised", "hospitalized", "admitted",
    "ambulance", "ambulances", "fire", "fires",
    "hazard", "hazards", "hazardous", "fell", "falling", "fallen",
    "collapse", "collapsed", "collapsing",
]

IMMINENT_KEYWORDS = [
    "imminent", "immediately", "danger", "dangerous", "dangerously", "risk",
    "risky", "live wire", "exposed wire", "spark", "sparks", "sparking",
    "electrical", "electric", "open manhole", "uncovered manhole",
    "traffic accident", "near miss", "about to fall", "falling debris",
    "cave", "caves", "caved", "caving", "crumbling", "gas leak", "leaking gas",
]

LOW_KEYWORDS = [
    "cosmetic", "minor", "aesthetic", "slight", "slightly", "superficial",
    "tiny", "negligible", "not urgent", "low priority", "small",
]

CATEGORY_KEYWORDS = [
    ("Heritage Damage", [
        "heritage", "monument", "fort", "palace", "temple", "statue",
        "historical", "historic", "archaeological",
    ]),
    ("Flooding", [
        "flood", "waterlog", "stagnant water", "water accumulation",
        "rain water", "inundat", "waterlogged",
    ]),
    ("Drain Blockage", [
        "drain", "drainage", "sewer", "sewage", "manhole", "clogged",
        "clogging", "choked", "choking", "open drain",
    ]),
    ("Heat Hazard", [
        "heat", "heatwave", "heat wave", "sunstroke", "heatstroke",
        "high temperature", "scorching",
    ]),
    ("Pothole", [
        "pothole", "hole in the road", "potholed", "crater",
    ]),
    ("Road Damage", [
        "road damage", "broken road", "damaged road", "road crack",
        "crack in the road", "cracked road", "pavement crack", "cracked",
        "road surface", "asphalt", "uneven road", "worn out road",
        "deteriorating road",
    ]),
    ("Streetlight", [
        "streetlight", "streetlamp", "street light", "lamp post",
        "lamppost", "lamp", "lighting", "light", "glow",
    ]),
    ("Waste", [
        "waste", "garbage", "litter", "trash", "rubbish", "dump", "dumping",
        "debris", "refuse", "bin", "solid waste", "garbage collection",
        "garbage pile",
    ]),
    ("Noise", [
        "noise", "loud", "horn", "honk", "honking", "music", "cacophony",
        "sound pollution", "loudspeaker", "disturbance", "disturbing noise",
    ]),
]

_SUFFIX = r"(?:s|es|ed|ing|d|en)?"
_CATEGORY_ORDER = [c for c, _ in CATEGORY_KEYWORDS]


def _contains(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase)
    if " " in phrase:
        return re.search(r"\b" + escaped + r"\b", text) is not None
    return re.search(r"\b" + escaped + _SUFFIX + r"\b", text) is not None


def _find_text_column(row: dict):
    lowered = {k.lower().replace(" ", "_").replace("-", "_"): k for k in row}
    for candidate in ("description", "complaint", "complaint_description",
                      "details", "text", "issue", "remarks"):
        if candidate in lowered:
            return lowered[candidate]
    for col in row:
        if "desc" in col.lower() or "complaint" in col.lower():
            return col
    return None


def _fallback_id(row: dict) -> str:
    for key in ("complaint_id", "id", "complaintid"):
        if key in row and row[key]:
            return str(row[key])
    for value in row.values():
        if value:
            return str(value)
    return "unknown"


def _classify_category(text: str):
    matches = []
    for idx, (cat, phrases) in enumerate(CATEGORY_KEYWORDS):
        for phrase in phrases:
            if _contains(text, phrase):
                matches.append((idx, cat, phrase))
    if not matches:
        return "Other", []
    counts = {}
    for idx, cat, phrase in matches:
        entry = counts.setdefault(cat, [idx, 0, []])
        entry[1] += 1
        entry[2].append(phrase)
    best_cat = max(counts, key=lambda c: (counts[c][1], -counts[c][0]))
    return best_cat, counts[best_cat][2]


def _classify_priority(text: str):
    for keyword in SEVERITY_KEYWORDS:
        if _contains(text, keyword):
            return "Urgent", ("the severity keyword", keyword)
    for keyword in IMMINENT_KEYWORDS:
        if _contains(text, keyword):
            return "Urgent", ("the imminent-risk phrase", keyword)
    for keyword in LOW_KEYWORDS:
        if _contains(text, keyword):
            return "Low", ("the low-severity phrase", keyword)
    return "Standard", None


def _build_reason(category: str, priority: str, cat_phrases, pri_evidence) -> str:
    if cat_phrases:
        clause = "mentions " + ", ".join("'%s'" % p for p in cat_phrases[:3])
    else:
        clause = "matches no category keywords"
    if pri_evidence:
        kind, keyword = pri_evidence
        clause += f" and contains {kind} '{keyword}'"
    if category == "Other" and not cat_phrases:
        return (f"The description {clause}, so category is Other and the row "
                "is flagged NEEDS_REVIEW.")
    return f"The description {clause}, so category is {category} and priority is {priority}."


def classify_complaint(row: dict) -> dict:
    text_col = _find_text_column(row)
    description = (row.get(text_col) if text_col else "") or ""
    text = " " + description.strip().lower() + " "
    if not description.strip():
        return {
            "complaint_id": _fallback_id(row),
            "category": "Other",
            "priority": "Standard",
            "reason": "The description is empty, so category and priority cannot be determined.",
            "flag": "NEEDS_REVIEW",
        }
    category, cat_phrases = _classify_category(text)
    priority, pri_evidence = _classify_priority(text)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    reason = _build_reason(category, priority, cat_phrases, pri_evidence)
    return {
        "complaint_id": _fallback_id(row),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _read_rows(input_path: str):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(input_path, "r", encoding=encoding, newline="") as fh:
                return list(csv.DictReader(fh))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {input_path}")


def batch_classify(input_path: str, output_path: str):
    rows = _read_rows(input_path)
    results = []
    for index, row in enumerate(rows, start=1):
        try:
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append({
                "complaint_id": _fallback_id(row),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row {index} failed to classify: {exc}",
                "flag": "NEEDS_REVIEW",
            })
    with open(output_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

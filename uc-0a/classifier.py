"""
UC-0A — Complaint Classifier

Transcribes the enforcement rules in agents.md (E1-E14) and the two skills in
skills.md (classify_complaint, batch_classify) into a deterministic classifier.
Every value emitted is drawn from closed, checkable lists.
"""
import argparse
import csv
import os
import re

CATEGORIES = (
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
PRIORITIES = ("Urgent", "Standard", "Low")
FLAG = "NEEDS_REVIEW"
FALLBACK = {"category": "Other", "priority": "Standard", "flag": FLAG}

OUTPUT_HEADER = ["complaint_id", "category", "priority", "reason", "flag"]

SEVERITY_STEMS = (
    ("injur", "injury"),
    ("child", "child"),
    ("school", "school"),
    ("hospital", "hospital"),
    ("ambul", "ambulance"),
    ("fire", "fire"),
    ("hazard", "hazard"),
    ("fell", "fell"),
    ("fall", "fell"),
    ("collaps", "collapse"),
)

UNLISTED_SIGNALS = (
    "gas leak",
    "live wire",
    "exposed wiring",
    "wiring theft",
    "burn",
    "unsafe",
)

HERITAGE_SUBJECT = ("heritage", "historic", "historical", "ancient", "museum", "monument", "old city")
HERITAGE_DAMAGE = ("knocked over", "defaced", "broken up", "not replaced", "damaged", "vandal", "demolished", "collapsed")

POTHOLE_PATTERN = re.compile(r"\b(potholes?|craters?|holes?)\b", re.IGNORECASE)
TEMPERATURE_PATTERN = re.compile(r"(\d{2,3})\s*[°]?\s*c", re.IGNORECASE)
FLOOD_RISK_PATTERN = re.compile(r"flooding risk|flood risk|prone to flood", re.IGNORECASE)

FLOOD_TERMS = ("flooded", "flooding", "floods", "flood", "waterlogged", "knee-deep", "submerged", "standing in water", "inundated")
ROAD_DAMAGE_TERMS = ("crack", "sink", "subsid", "buckl", "upturned", "bubbl", "melt", "collaps", "broken footpath", "broken tiles")
STREETLIGHT_TERMS = ("streetlight", "street light", "lights out", "unlit", "dark", "wiring theft", "substation", "flicker", "spark")
WASTE_TERMS = ("garbage", "waste", "overflow", "not cleared", "dead animal", "bins", "rubbish", "litter", "debris dumped", "not removed")
NOISE_TERMS = ("music", "band", "drill", "amplif", "idling", "engine", "midnight", "loud", "horn")
HEAT_WORDS = ("heatwave", "storing heat", "unbearable", "exposed to full sun", "burn")

DRAIN_TERMS = ("drain", "stormwater", "manhole", "sewer")
DRAIN_BLOCKERS = ("block", "clogg", "choke")

STANDARD_MARKERS = (
    "blocked", "clogg", "overflow", "spark", "not removed", "not cleared",
    "unlit", "darkness", "dark", "collaps", "stranded", "abandoned", "exposed",
    "health", "risk", "crack", "sink", "subsid", "pothole", "crater", "hole",
    "knocked over", "broken", "buckl", "melt", "bubbl", "dead animal", "burn",
    "heat", "temperature", "flood",
)

PUBLIC_ASSET_DEFECTS = ("manhole", "glass", "irrigation", "tree")
PUBLIC_ASSET_PATTERNS = [
    re.compile(r"\bmanholes?\b"),
    re.compile(r"\bglass\b"),
    re.compile(r"\birrigation\b"),
    re.compile(r"\btrees?\b"),
]


def _verbatim_span(original: str, term: str | None, radius: int = 2) -> str:
    """A verbatim one-sentence window of the description around the evidence term."""
    tokens = [(m.group(), m.start()) for m in re.finditer(r"\S+", original)]
    if not tokens:
        return (original.strip() or "unclassified.")[:40] + "."
    lo = original.lower()
    hit = None
    if term:
        key = term.split()[0]
        hit = next((t for t, _ in tokens if key.lower() in t.lower()), None)
    if hit is None:
        hit = next((t for t, _ in tokens), original.strip()[:20])
        if not hit.strip():
            return "unclassified."
    idx = next(i for i, (t, _) in enumerate(tokens) if t == hit)
    selected = tokens[max(0, idx - radius): idx + radius + 1]
    window = " ".join(t for t, _ in selected)
    sentences = re.split(r"(?<=[.!?])\s+", window)
    if term and hit:
        span = next((s for s in sentences if hit.lower() in s.lower()), sentences[0])
    else:
        span = sentences[0]
    span = span.strip(" .,;:")
    return span or hit or "unclassified"


def _matching_token(original: str, term: str):
    return next((t for t in re.findall(r"\S+", original) if term.lower() in t.lower()), None)


def _severity_present(text: str):
    return [(stem, word) for stem, word in SEVERITY_STEMS if stem in text]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row (skills.md classify_complaint).
    Returns: dict with keys: complaint_id, category, priority, reason, flag.
    Never raises: an empty description or a failure to match any rule still
    produces a closed-list result, per agents.md E11/E14.
    """
    cid = row.get("complaint_id")
    cid = str(cid) if cid is not None else ""
    desc = row.get("description")
    if not isinstance(desc, str):
        desc = str(desc) if desc is not None else ""
    if not desc.strip():
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description field is empty or unreadable.",
            "flag": FLAG,
        }

    text = desc.lower()

    severity_hits = _severity_present(text)
    if severity_hits:
        priority = "Urgent"
    elif any(marker in text for marker in STANDARD_MARKERS):
        priority = "Standard"
    else:
        priority = "Low"

    unlisted = next((s for s in UNLISTED_SIGNALS if s in text), None)

    category, term = "Other", None
    heritage_subject = any(t in text for t in HERITAGE_SUBJECT)
    heritage_hit = any(t in text for t in HERITAGE_DAMAGE)
    if heritage_subject and heritage_hit:
        category, term = "Heritage Damage", next(t for t in HERITAGE_DAMAGE if t in text)
    elif POTHOLE_PATTERN.search(desc):
        category, term = "Pothole", POTHOLE_PATTERN.search(desc).group(1)
    elif not FLOOD_RISK_PATTERN.search(text) and any(t in text for t in FLOOD_TERMS):
        category, term = "Flooding", next(t for t in FLOOD_TERMS if t in text)
    elif any(t in text for t in ROAD_DAMAGE_TERMS):
        category, term = "Road Damage", next(t for t in ROAD_DAMAGE_TERMS if t in text)
    elif any(t in text for t in STREETLIGHT_TERMS):
        category, term = "Streetlight", next(t for t in STREETLIGHT_TERMS if t in text)
    elif any(t in text for t in WASTE_TERMS):
        category, term = "Waste", next(t for t in WASTE_TERMS if t in text)
    elif any(t in text for t in NOISE_TERMS):
        category, term = "Noise", next(t for t in NOISE_TERMS if t in text)
    elif any(t in text for t in HEAT_WORDS):
        category, term = "Heat Hazard", next(t for t in HEAT_WORDS if t in text)
    elif TEMPERATURE_PATTERN.search(text):
        matched = TEMPERATURE_PATTERN.search(text)
        if int(matched.group(1)) >= 40:
            category, term = "Heat Hazard", matched.group(0)
    elif any(t in text for t in DRAIN_TERMS) and any(b in text for b in DRAIN_BLOCKERS):
        category, term = "Drain Blockage", next(b for b in DRAIN_BLOCKERS if b in text)

    span = _verbatim_span(desc, term)

    if category == "Other":
        reason = f"Classified as Other because the description says {span} and matches no taxonomy rule."
        flag = FLAG
    elif unlisted:
        reason = (f"Classified as {category} with {priority} priority because the description says {span}"
                  f" but lists unlisted hazard {unlisted} for review.")
        flag = FLAG
    elif severity_hits:
        word = _matching_token(desc, severity_hits[0][0]) or severity_hits[0][1]
        reason = (f"Classified as {category}, priority {priority} because the description says {span}"
                  f" and contains severity word {word}.")
        flag = ""
    else:
        reason = f"Classified as {category} because the description says {span}."
        flag = ""

    heritage_qualifier = any(t in text for t in HERITAGE_SUBJECT) and category != "Heritage Damage"
    asset_defect = any(p.search(text) for p in PUBLIC_ASSET_PATTERNS)
    if flag != FLAG and (heritage_qualifier or asset_defect):
        flag = FLAG

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _coerce(value, allowed, fallback):
    """agents.md E14: never emit a value outside the closed lists."""
    return value if value in allowed else fallback


def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV (skills.md batch_classify).
    Returns dict with keys: rows_read, rows_written, rows_flagged.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", newline="", encoding="utf-8") as f:
        input_rows = list(csv.DictReader(f))

    results = []
    for row in input_rows:
        try:
            result = classify_complaint(row)
        except Exception as exc:  # noqa: BLE001
            cid = row.get("complaint_id") if row else None
            result = {
                "complaint_id": str(cid) if cid is not None else "",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row could not be classified: {type(exc).__name__}.",
                "flag": "NEEDS_REVIEW",
            }
        result["category"] = _coerce(result["category"], CATEGORIES, "Other")
        result["priority"] = _coerce(result["priority"], PRIORITIES, "Standard")
        result["flag"] = result["flag"] if result["flag"] in ("", FLAG) else ""
        results.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_HEADER)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"] == FLAG)
    return {"rows_read": len(input_rows), "rows_written": len(results), "rows_flagged": flagged}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    counts = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
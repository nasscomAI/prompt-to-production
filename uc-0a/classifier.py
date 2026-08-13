"""
UC-0A — Complaint Classifier
Implementation guided by agents.md (RICE) and skills.md, per the CRAFT workflow.

Enforcement rules implemented (see agents.md):
  R1  Category must be exactly one of the 10 allowed strings — no variations, no sub-categories.
  R2  Priority must be Urgent if the description contains any severity keyword
      (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
  R3  Every output row includes a reason field citing specific words from the description.
  R4  If the category cannot be determined from the description alone ->
      category: Other, flag: NEEDS_REVIEW. Never guess with false confidence.

Skills implemented (see skills.md):
  classify_complaint  — one complaint row in -> {complaint_id, category, priority, reason, flag} out
  batch_classify      — reads input CSV, applies classify_complaint per row, writes output CSV
"""
import argparse
import csv

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

# R2 — severity keywords that MUST trigger Urgent priority
# Base list from README: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
# CRAFT fix: "gas leak" (fire/explosion hazard) and "collapsing" (form of collapse) were
# missed by the naive list — a leak/collapse in progress is Urgent, not Standard.
SEVERITY_KEYWORDS = (
    "injury", "injured", "child", "children", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse", "collapsed", "collapsing",
    "gas leak", "gas leakage",
)

# R1 — category rules: (allowed category, keyword triggers). First match wins.
# Order matters: most specific rules are checked first so a description like
# "Heritage street, lights out" lands on Streetlight, not Heritage Damage.
CATEGORY_RULES = [
    ("Pothole",        ["pothole", "potholes"]),
    ("Streetlight",    ["streetlight", "street light", "lights out", "unlit", "substation",
                        "power cut", "power outage", "lamp post",
                        "lamppost", "street lamp"]),
    ("Noise",          ["noise", "noisy", "loudspeaker", "loud speaker", "loud music", "music",
                        "band playing", "drilling", "construction noise", "idling",
                        "honking", "horn", "loud engine"]),
    ("Flooding",       ["flooded", "flooding", "floods", "flood", "waterlogged",
                        "water-logged", "waterlogging", "water-logging"]),
    ("Drain Blockage", ["drain", "drainage"]),
    ("Waste",          ["garbage", "rubbish", "trash", "waste", "dead animal",
                        "litter", "dumped", "dump", "bins"]),
    ("Road Damage",    ["road surface", "road damage", "cracked", "sinking", "subsided",
                        "subsidence", "crater", "collapsed", "collapse", "collapsing",
                        "footpath", "pavement", "manhole", "broken tiles", "upturned"]),
    ("Heritage Damage",["heritage", "heritage structure", "historic", "monument"]),
    ("Heat Hazard",    ["heat", "heatwave", "heat wave", "sunstroke", "melting",
                        "unbearable temperature", "dangerous temperature", "full sun",
                        "°c"]),
]

# Low-impact markers for priority decisions when no severity keyword is present
LOW_IMPACT_MARKERS = (
    "minor", "cosmetic", "small", "slight", "occasional",
    "single streetlight", "one streetlight",
)

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _snippet(description: str, keyword: str, radius: int = 55) -> str:
    """Return a short slice of the description centred on the matched keyword."""
    idx = description.lower().find(keyword)
    if idx == -1:
        return description[:120] + ("…" if len(description) > 120 else "")
    start = max(0, idx - radius)
    end = min(len(description), idx + len(keyword) + radius)
    snippet = description[start:end].strip()
    return snippet + "…" if end < len(description) else snippet


def _matched_text(description: str, keyword: str) -> str:
    """R3 — return the keyword exactly as written in the description (original case)."""
    idx = description.lower().find(keyword)
    if idx == -1:
        return keyword
    return description[idx:idx + len(keyword)]


def _match_category(description_lower: str):
    """R1 — return (category, matched_keyword) or (None, None) if no rule matches."""
    for category, keywords in CATEGORY_RULES:
        for keyword in keywords:
            if keyword in description_lower:
                return category, keyword
    return None, None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Skills contract (skills.md): never raises on missing fields — a row without a
    usable description is returned flagged NEEDS_REVIEW with an explanatory reason.
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = row.get("description")

    if description is None or not str(description).strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description present — cannot classify without text to cite",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()
    description_lower = description.lower()

    # R2 — severity triggers decide priority, independent of category
    triggers = [kw for kw in SEVERITY_KEYWORDS if kw in description_lower]

    # R1 + R4 — exact category from the allowed list, or Other + NEEDS_REVIEW
    category, matched_keyword = _match_category(description_lower)
    ambiguous = category is None
    if ambiguous:
        category = "Other"

    # R3 — reason must cite specific words from the description
    if ambiguous:
        reason = (
            f'No allowed category keyword found in the description '
            f'("{_snippet(description, "notfound")}") — category cannot be determined, '
            f"so it is marked NEEDS_REVIEW"
        )
    elif triggers:
        reason = (
            f'The description mentions "{_matched_text(description, matched_keyword)}" '
            f'("{_snippet(description, matched_keyword)}"), '
            f"so the category is {category}; severity trigger(s) "
            f"{', '.join(triggers)} make the priority Urgent"
        )
    else:
        reason = (
            f'The description mentions "{_matched_text(description, matched_keyword)}" '
            f'("{_snippet(description, matched_keyword)}"), '
            f"so the category is {category}"
        )

    if triggers:
        priority = "Urgent"
    elif any(marker in description_lower for marker in LOW_IMPACT_MARKERS):
        priority = "Low"
    else:
        priority = "Standard"

    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Skills contract (skills.md): flags malformed rows as NEEDS_REVIEW instead of
    crashing, skips no rows, always produces the output file, and raises a clear
    error only when the input file is missing or unreadable.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Input file {input_path} is empty (no header row)")
            rows = list(reader)
    except OSError as exc:
        raise FileNotFoundError(f"Cannot read input file {input_path}: {exc}") from exc

    results = []
    failed = 0
    for index, raw in enumerate(rows, start=1):
        try:
            results.append(classify_complaint(raw))
        except Exception as exc:  # defensive — a bad row must never kill the batch
            failed += 1
            results.append({
                "complaint_id": str(raw.get("complaint_id", f"row-{index}")).strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Row {index} could not be processed ({exc})",
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    urgent = sum(1 for r in results if r["priority"] == "Urgent")
    review = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Classified {len(results)} complaints -> {output_path}")
    print(f"  Urgent: {urgent} | NEEDS_REVIEW: {review} | unprocessable rows: {failed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

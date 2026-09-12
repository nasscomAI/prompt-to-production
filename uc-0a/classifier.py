"""
UC-0A — Complaint Classifier
Deterministic rule-based classifier implementing the enforcement rules from
agents.md (exact category strings, severity-keyword urgency, cited reasons,
NEEDS_REVIEW on genuine ambiguity) and the skills from skills.md.
"""
import argparse
import csv
import re

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

# category -> (precedence, keywords)
# A trailing "*" marks a stem prefix (matches any word starting with it).
# Dominant keywords identify the subject of the complaint even under ties.
KEYWORDS = {
    "Pothole": (10, ["pothole*", "pot hole", "pot-hole"]),
    "Flooding": (9, ["flood*", "waterlogg*", "submerged", "standing in water", "inundat*", "rainwater"]),
    "Heat Hazard": (8, ["heat*", "temperature*", "°c", "melting", "bubbl*", "scorch*", "burn*", "unbearable", "sun"]),
    "Streetlight": (7, ["streetlight", "lamp post", "lights out", "lighting", "dark*", "unlit", "substation", "flicker*"]),
    "Drain Blockage": (6, ["drain*", "manhole", "culvert", "sewer", "blocked"]),
    "Road Damage": (5, ["crack*", "sink*", "subsid*", "collaps*", "buckle*", "footpath", "paving", "road surface", "erosion"]),
    "Waste": (4, ["garbage", "trash", "litter", "overflow", "waste", "dump*", "dead animal", "bins"]),
    "Noise": (3, ["music", "nois*", "band", "amplifier*", "audio", "drill*", "idling", "loud", "honk*", "horn"]),
    "Heritage Damage": (2, ["heritage", "historic", "monument", "ancient", "museum", "cobblestone", "defac*"]),
    "Other": (1, []),
}

# severity triggers (agents.md: injury, child, school, hospital, ambulance,
# fire, hazard, fell, collapse) with stem variants where marked with "*".
SEVERITY_TERMS = [
    "injur*", "child*", "school", "hospital*", "ambulance",
    "fire", "hazard*", "fell", "fall risk", "collaps*", "burn*", "accident*",
]

def _token_hits(text: str, keywords):
    hits = []
    for kw in keywords:
        if kw.endswith("*"):
            pattern = r"\b" + re.escape(kw[:-1])
        else:
            pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text):
            hits.append(kw)
    return hits


def _category_scores(text: str):
    scores = {}
    for cat, (_prec, keywords) in KEYWORDS.items():
        if not keywords:
            continue
        hits = _token_hits(text, keywords)
        if hits:
            scores[cat] = (len(hits), hits)
    return scores


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "")
    if description is None:
        description = ""
    text = description.lower()

    scores = _category_scores(text)

    urgent_words, urgents = _severity_check(text)
    if urgents:
        priority = "Urgent"
    elif text and any(w in text for w in ["minor", "cosmetic", "slight"]):
        priority = "Low"
    else:
        priority = "Standard"

    if not scores:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "No category-defining words could be matched in the description.",
            "flag": "NEEDS_REVIEW",
        }

    ordered = sorted(
        scores.items(),
        key=lambda kv: (kv[1][0], KEYWORDS[kv[0]][0]),
        reverse=True,
    )
    best, best_info = ordered[0]
    second = ordered[1] if len(ordered) > 1 else None

    best_hits = best_info[1]
    dominant = KEYWORDS[best][1]
    dominant_hits = [h for h in best_hits if h in dominant]

    flag = ""
    if second is not None and best_info[0] == second[1][0] and not dominant_hits:
        flag = "NEEDS_REVIEW"

    quoted = ", ".join('"' + h + '"' for h in best_hits[:4])
    reason = f'Cited {quoted} in the complaint description => this is a {best} issue.'
    if urgents:
        reason += f' Severity trigger "{urgent_words[0]}" => Urgent priority.'
    if flag:
        reason += " Category is genuinely ambiguous between multiple complaint types; review recommended."

    return {
        "complaint_id": complaint_id,
        "category": best,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _severity_check(text: str):
    return _token_hits(text, SEVERITY_TERMS), any(_token_hits(text, SEVERITY_TERMS))


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, does not crash on bad rows, produces output even if some rows fail.
    """
    results = []
    failed = []

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input file is empty or missing a header row.")
        required = {"complaint_id", "description"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Input CSV missing required columns: {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            try:
                results.append(classify_complaint(row))
            except Exception as exc:
                failed.append((line_no, str(exc)))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)

    if failed:
        print(f"WARNING: {len(failed)} row(s) skipped. Details:")
        for line_no, exc in failed:
            print(f"  line {line_no}: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
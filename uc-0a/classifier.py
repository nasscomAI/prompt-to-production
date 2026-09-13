"""
UC-0A — Complaint Classifier
Deterministic, local, rule-based. Enforces the severity/urgency rules and the
exact category enum from skills.md / README. No external APIs or dependencies.
"""
import argparse
import csv
import re

CATEGORY_RULES = (
    ("Pothole",           ("pothole", "potholes")),
    ("Flooding",          ("flood", "flooded", "floods", "flooding", "knee-deep", "standing water", "submerged", "inundat", "waterlogged")),
    ("Streetlight",       ("streetlight", "streetlights", "street light", "street lights", "lights out", "lamp post", "lamp", "unlit", "substation", "dark", "darkness", "sparking")),
    ("Waste",             ("garbage", "waste", "bins", "rubbish", "dead animal", "refuse")),
    ("Heat Hazard",       ("temperature", "temperatures", "heat", "melting", "burn", "burns", "sun", "celsius", "\u00b0c")),
    ("Noise",             ("noise", "music", "drilling", "amplifier", "amplifiers", "idling", "band")),
    ("Heritage Damage",   ("heritage", "historic", "ancient", "museum", "step well", "cobblestone", "tram road")),
    ("Drain Blockage",    ("drain", "drains", "draining", "blocked", "blockage", "mosquito")),
    ("Road Damage",       ("pavement", "paving", "road surface", "cracked", "cracking", "sinking", "subsided", "subsidence", "buckled", "collapsed", "manhole", "footpath")),
)

URGENT_KEYWORDS = (
    "injury", "injured", "injuries",
    "child", "children",
    "school",
    "hospital", "hospitalised", "hospitalized",
    "ambulance",
    "fire",
    "hazard", "hazardous",
    "fell", "fall", "falling", "collapse", "collapsed", "collapsing",
    "serious",
    "immediate danger",
)

LOW_KEYWORDS = (
    "irrigation", "grass dying", "aesthetic",
)


def _find_term(description: str, keywords) -> str:
    text = description.lower()
    for kw in keywords:
        if re.fullmatch(r"[a-z]+", kw):
            pattern = rf"\b{re.escape(kw)}\b"
        else:
            pattern = re.escape(kw)
        found = re.search(pattern, text)
        if found:
            return found.group(0)
    return ""


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id")
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description; flagged NEEDS_REVIEW.",
            "flag": "NEEDS_REVIEW",
        }

    urgent_term = _find_term(description, URGENT_KEYWORDS)
    if urgent_term:
        priority = "Urgent"
        priority_note = f"Urgent because '{urgent_term}' is a severity keyword"
    elif _find_term(description, LOW_KEYWORDS):
        priority = "Low"
        priority_note = "Low because it states a minor cosmetic issue"
    else:
        priority = "Standard"
        priority_note = "Standard — no severity keyword present"

    category = "Other"
    category_term = ""
    for cat, keywords in CATEGORY_RULES:
        term = _find_term(description, keywords)
        if term:
            category = cat
            category_term = term
            break

    if category == "Other":
        reason = (
            f"Other — '{description[:90]}' matches no category in the enum; "
            "flagged NEEDS_REVIEW."
        )
    else:
        reason = f"{category} — description cites '{category_term}'; {priority_note}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "NEEDS_REVIEW" if category == "Other" else "",
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(input_path, "r", encoding="utf-8", newline="") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            result = classify_complaint(row)
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

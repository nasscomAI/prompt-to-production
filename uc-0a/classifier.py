"""
UC-0A Complaint Classifier.
"""
import argparse
import csv
import re
from pathlib import Path

SEVERITY_PATTERNS = {
    "injury": r"\binjur(?:y|ed)\b",
    "child": r"\bchild(?:ren)?\b",
    "school": r"\bschool\b",
    "hospital": r"\bhospital(?:ised|ized)?\b",
    "ambulance": r"\bambulance\b",
    "fire": r"\bfire\b",
    "hazard": r"\bhazard\b",
    "fell": r"\bfell\b",
    "fall": r"\bfall\b",
    "collapse": r"\bcollaps(?:e|ed)\b",
}

CATEGORY_RULES = [
    (
        "Heritage Damage",
        [
            r"\bheritage lamp post\b",
            r"\bhistoric tram road\b",
            r"\bancient step well\b",
            r"\bheritage (?:stone|building)\b",
            r"\bcobblestones?\b",
            r"\bdefaced\b",
            r"\bnot restored\b",
            r"\bbillboard installation\b",
        ],
    ),
    (
        "Pothole",
        [
            r"\bpothole(?:s)?\b",
            r"\btyre blowouts?\b",
            r"\btyre damage\b",
            r"\bmotorcycle wheel\b",
        ],
    ),
    (
        "Drain Blockage",
        [
            r"\bstormwater drain\b",
            r"\bmain drain blocked\b",
            r"\bdrain (?:completely )?blocked\b",
            r"\bdrainage blocked\b",
            r"\bdrain 100% blocked\b",
            r"\bblocked with construction debris\b",
        ],
    ),
    (
        "Heat Hazard",
        [
            r"\bheatwave\b",
            r"\btemperature\b",
            r"\btemperatures\b",
            r"\bmelting\b",
            r"\bbubbling\b",
            r"\bburns?\b",
            r"\bunbearable\b",
            r"\bfull sun\b",
            r"\bunsafe\b",
        ],
    ),
    (
        "Flooding",
        [
            r"\bflood(?:ed|ing|s)?\b",
            r"\brainwater\b",
            r"\bstanding in water\b",
            r"\bstranded\b",
            r"\bunderpass\b",
        ],
    ),
    (
        "Waste",
        [
            r"\bwaste\b",
            r"\bgarbage\b",
            r"\bbins?\b",
            r"\boverflow(?:ing)?\b",
            r"\bnot cleared\b",
            r"\bdumped\b",
            r"\bdead animal\b",
        ],
    ),
    (
        "Noise",
        [
            r"\bnoise\b",
            r"\bmusic\b",
            r"\bdrilling\b",
            r"\bidling\b",
            r"\bamplifiers?\b",
            r"\baudible\b",
            r"\bengines on\b",
        ],
    ),
    (
        "Streetlight",
        [
            r"\bstreetlights?\b",
            r"\blights out\b",
            r"\bunlit\b",
            r"\bdark(?:ness)?\b",
            r"\bflickering\b",
            r"\bsparking\b",
            r"\bsubstation tripped\b",
        ],
    ),
    (
        "Road Damage",
        [
            r"\broad collapse(?:d)?\b",
            r"\bcollapse(?:d)?\b",
            r"\bcrater\b",
            r"\bcracked\b",
            r"\bsinking\b",
            r"\bsubsidence\b",
            r"\bsubsided\b",
            r"\bbuckled\b",
            r"\bmanhole\b",
            r"\bfootpath\b",
            r"\bpaving\b",
            r"\broad surface\b",
            r"\bupturned\b",
            r"\bbridge\b",
            r"\bmissing\b",
        ],
    ),
]

EXTRA_URGENT_PATTERNS = [
    r"\blives at risk\b",
    r"\baccident risk\b",
    r"\bhealth risk\b",
    r"\bgas leak\b",
    r"\bstructural concern\b",
]


def normalize_text(value: str) -> str:
    normalized = value.casefold()
    for token in ("—", "–", "â€”", "â€“"):
        normalized = normalized.replace(token, " ")
    return normalized


def collect_matches(patterns: list[str], text: str) -> list[str]:
    matches = []
    for pattern in patterns:
        found = re.search(pattern, text)
        if found:
            matches.append(found.group(0))
    return matches


def detect_category(description: str) -> tuple[str, list[str], str]:
    text = normalize_text(description)
    scores = []
    for category, patterns in CATEGORY_RULES:
        matches = collect_matches(patterns, text)
        if matches:
            scores.append((category, len(matches), matches))

    if not scores:
        return "Other", [], "No category keyword matched strongly enough"

    scores.sort(key=lambda item: -item[1])
    top_category, top_score, top_matches = scores[0]
    if top_score < 1:
        return "Other", top_matches, "Description is ambiguous across multiple categories"
    return top_category, top_matches, ""


def detect_priority(description: str, category: str) -> tuple[str, list[str]]:
    text = normalize_text(description)
    hits = []
    for pattern in list(SEVERITY_PATTERNS.values()) + EXTRA_URGENT_PATTERNS:
        found = re.search(pattern, text)
        if found:
            hits.append(found.group(0))
    if hits:
        return "Urgent", hits
    if category == "Other":
        return "Low", []
    return "Standard", []


def build_reason(category: str, priority: str, category_hits: list[str], priority_hits: list[str], flag: str) -> str:
    cited = []
    seen = set()
    for hit in category_hits + priority_hits:
        cleaned = hit.strip()
        if cleaned and cleaned not in seen:
            cited.append("'" + cleaned + "'")
            seen.add(cleaned)
    if not cited:
        cited = ["no strong category keyword"]

    reason = f"Category set to {category} from {', '.join(cited)}."
    if priority == "Urgent" and priority_hits:
        urgent_citations = ", ".join("'" + hit + "'" for hit in priority_hits[:3])
        reason += f" Priority is Urgent because of {urgent_citations}."
    elif priority == "Low" and flag:
        reason += " Priority is Low because the complaint needs manual review."
    else:
        reason += f" Priority is {priority} because no severity trigger was found."
    return reason


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = (row.get("description") or "").strip()
    complaint_id = (row.get("complaint_id") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Category set to Other because the description is blank; manual review is required.",
            "flag": "NEEDS_REVIEW",
        }

    category, category_hits, ambiguity_reason = detect_category(description)
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    priority, priority_hits = detect_priority(description, category)
    reason = build_reason(category, priority, category_hits, priority_hits, flag)
    if ambiguity_reason:
        reason = f"{reason} {ambiguity_reason}."

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
    """
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8", newline="") as infile:
        rows = list(csv.DictReader(infile))

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with output_file.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": (row.get("complaint_id") or "").strip(),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Category set to Other because classification failed with '{type(exc).__name__}'; manual review is required.",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

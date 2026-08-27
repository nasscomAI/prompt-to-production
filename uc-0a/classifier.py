"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import csv
from typing import Dict, List, Tuple

ALLOWED_CATEGORIES: List[str] = [
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

VALID_PRIORITIES = {"Urgent", "Standard", "Low"}

SEVERITY_KEYWORDS = {
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
}

CATEGORY_KEYWORDS = {
    "Pothole": [
        "pothole",
        "potholes",
        "crater",
        "road pit",
        "pit in road",
    ],
    "Flooding": [
        "flood",
        "flooding",
        "flooded",
        "waterlogged",
        "water logging",
        "submerged",
        "underpass floods",
        "underpass flooded",
        "rainwater",
        "water accumulation",
    ],
    "Streetlight": [
        "streetlight",
        "street light",
        "lamp post",
        "lamp",
        "no light",
        "dark road",
        "dark street",
        "street lights not working",
    ],
    "Waste": [
        "waste",
        "garbage",
        "trash",
        "litter",
        "dump",
        "dumping",
        "overflowing bin",
        "bin overflow",
        "garbage overflow",
        "piles of waste",
        "waste not cleared",
    ],
    "Noise": [
        "noise",
        "loudspeaker",
        "loud music",
        "construction noise",
        "construction drilling",
        "drilling",
        "idling",
        "honking",
        "horn",
        "disturbance",
        "engines on",
    ],
    "Road Damage": [
        "road damage",
        "broken road",
        "damaged road",
        "cracked road",
        "road cracked",
        "road surface damaged",
        "road caved",
        "road condition poor",
    ],
    "Heritage Damage": [
        "heritage damage",
        "monument damage",
        "historic wall damage",
        "temple wall damage",
        "statue damage",
        "damage to monument",
        "damage to heritage",
    ],
    "Heat Hazard": [
        "heat",
        "heatwave",
        "extreme heat",
        "hot zone",
        "no shade",
        "sun exposure",
        "heat hazard",
    ],
    "Drain Blockage": [
        "drain",
        "blocked drain",
        "clogged drain",
        "stormwater drain",
        "storm water drain",
        "drainage",
        "drain blocked",
        "manhole overflow",
        "sewer",
        "construction debris",
    ],
}


def normalize_text(text: str) -> str:
    """Clean whitespace and replace common bad characters."""
    if text is None:
        return ""
    text = str(text)
    text = text.replace("a€\"", "-")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    return text.strip()


def get_description(row: Dict[str, str]) -> str:
    """Find complaint text from common column names."""
    preferred_keys = {
        "description",
        "complaint",
        "complaint_text",
        "text",
        "issue",
        "details",
    }

    for key in row.keys():
        if key.strip().lower() in preferred_keys:
            return normalize_text(row.get(key, ""))

    values = [normalize_text(v) for v in row.values() if normalize_text(v)]
    return max(values, key=len) if values else ""


def get_complaint_id(row: Dict[str, str], row_index: int) -> str:
    """Use existing complaint id if present, else create fallback."""
    id_keys = {"complaint_id", "id", "ticket_id", "case_id"}

    for key in row.keys():
        if key.strip().lower() in id_keys:
            value = normalize_text(row.get(key, ""))
            if value:
                return value

    return f"row_{row_index}"


def classify_priority(text: str) -> str:
    """Assign priority using severity keywords first."""
    lowered = text.lower()

    if any(keyword in lowered for keyword in SEVERITY_KEYWORDS):
        return "Urgent"

    low_keywords = {
        "minor",
        "small",
        "slight",
        "not urgent",
        "whenever possible",
        "low priority",
    }
    if any(keyword in lowered for keyword in low_keywords):
        return "Low"

    return "Standard"


def classify_category(text: str) -> Tuple[str, str]:
    """
    Return (category, flag).
    If clearly matched to one category, return that category and blank flag.
    If ambiguous or no match, return Other and NEEDS_REVIEW.
    """
    lowered = text.lower()

    # Strong direct rules first
    if (
        "main drain blocked" in lowered
        or "drain blocked" in lowered
        or "blocked drain" in lowered
        or "clogged drain" in lowered
        or "stormwater drain" in lowered
        or "storm water drain" in lowered
    ):
        return "Drain Blockage", ""

    if (
        "garbage overflow" in lowered
        or "waste not cleared" in lowered
        or "overflowing bin" in lowered
        or "piles of waste" in lowered
    ):
        return "Waste", ""

    if (
        "construction drilling" in lowered
        or "loudspeaker" in lowered
        or "loud music" in lowered
        or "idling with engines on" in lowered
        or "honking" in lowered
    ):
        return "Noise", ""

    if (
        "underpass floods" in lowered
        or "underpass flooded" in lowered
        or "market area flooded" in lowered
        or "waterlogged" in lowered
        or "flooding" in lowered
        or "flooded" in lowered
    ):
        return "Flooding", ""

    scores: Dict[str, int] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in lowered)
        if score > 0:
            scores[category] = score

    if not scores:
        return "Other", "NEEDS_REVIEW"

    sorted_matches = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_category, top_score = sorted_matches[0]

    if len(sorted_matches) == 1:
        return top_category, ""

    second_score = sorted_matches[1][1]

    if top_score > second_score:
        return top_category, ""

    return "Other", "NEEDS_REVIEW"


def build_reason(text: str, category: str, priority: str, flag: str) -> str:
    """Build one-sentence reason citing words from description."""
    lowered = text.lower()
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in lowered]

    snippet = " ".join(text.split()[:8]).strip(" .,;:-")
    if not snippet:
        snippet = "insufficient complaint text"

    if severity_hits:
        cited = ", ".join(severity_hits[:2])
        return (
            f"Marked as {priority} because the description includes '{cited}' "
            f"and indicates a {category.lower()} issue."
        )

    if flag == "NEEDS_REVIEW":
        return (
            f"Marked for review because the description '{snippet}' "
            f"is not specific enough for a confident category."
        )

    return f"Marked as {category} because the description mentions '{snippet}'."


def classify_complaint(row: Dict[str, str], row_index: int = 0) -> Dict[str, str]:
    """
    Classify a single complaint row.
    Returns keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = get_complaint_id(row, row_index)
    description = normalize_text(get_description(row))

    if not description:
        return {
            "complaint_id": complaint_id.strip(),
            "category": "Other",
            "priority": "Low",
            "reason": "Marked for review because the description is missing or empty.",
            "flag": "NEEDS_REVIEW",
        }

    category, flag = classify_category(description)
    priority = classify_priority(description)
    reason = build_reason(description, category, priority, flag)

    # Final schema enforcement
    category = normalize_text(category)
    priority = normalize_text(priority)
    flag = normalize_text(flag)
    reason = " ".join(reason.split()).strip()

    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    if priority not in VALID_PRIORITIES:
        priority = "Standard"

    if flag and flag != "NEEDS_REVIEW":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": str(complaint_id).replace('"', "").replace("'", "").strip(),
        "category": str(category).replace('"', "").replace("'", "").strip(),
        "priority": str(priority).replace('"', "").replace("'", "").strip(),
        "reason": " ".join(str(reason).split()).strip(),
        "flag": str(flag).replace('"', "").replace("'", "").strip(),
    }


def batch_classify(input_path: str, output_path: str) -> None:
    """
    Read input CSV, classify rows, and write output CSV safely.
    Must not crash on malformed rows.
    """
    results = []

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        for idx, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row, idx)
            except Exception:
                result = {
                    "complaint_id": f"row_{idx}",
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Marked for review because the row could not be processed reliably.",
                    "flag": "NEEDS_REVIEW",
                }

            cleaned = {
                "complaint_id": str(result.get("complaint_id", f"row_{idx}")).replace('"', "").replace("'", "").strip(),
                "category": str(result.get("category", "Other")).replace('"', "").replace("'", "").strip(),
                "priority": str(result.get("priority", "Standard")).replace('"', "").replace("'", "").strip(),
                "reason": " ".join(
                    str(result.get("reason", "")).replace('"', "").replace("'", "'").split()
                ).strip(),
                "flag": str(result.get("flag", "")).replace('"', "").replace("'", "").strip(),
            }

            if cleaned["category"] not in ALLOWED_CATEGORIES:
                cleaned["category"] = "Other"
                cleaned["flag"] = "NEEDS_REVIEW"

            if cleaned["priority"] not in VALID_PRIORITIES:
                cleaned["priority"] = "Standard"

            if cleaned["flag"] not in {"", "NEEDS_REVIEW"}:
                cleaned["flag"] = "NEEDS_REVIEW"

            results.append(cleaned)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
"""
UC-0A — Complaint Classifier
Implement the UC-0A README classification schema in a way that remains
verifiable and safe on ambiguous descriptions.
"""
import argparse
import csv
import os
import re


ALLOWED_CATEGORIES = {
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
}

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

CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "pot hole", "tyre damage", "road depression"],
    "Flooding": ["flood", "flooded", "waterlogged", "standing water", "inundated", "water logging", "submerged"],
    "Streetlight": ["streetlight", "street light", "streetlights", "street lights", "light out", "lights out", "lamp post", "lamppost", "sparking"],
    "Waste": ["garbage", "garbage bins", "waste", "bulk waste", "overflowing bins", "dumped", "spillage"],
    "Noise": ["noise", "music", "loud", "midnight", "disturbance", "sound"],
    "Road Damage": ["road cracked", "road damage", "surface cracked", "footpath", "tiles broken", "upturned", "sinking", "broken road", "road surface", "crack"],
    "Heritage Damage": ["heritage", "heritage street", "heritage building", "heritage wall"],
    "Heat Hazard": ["heat", "temperature", "sun", "hot weather", "hotspot"],
    "Drain Blockage": ["drain", "drainage", "manhole", "blocked drain", "clogged drain", "sewer", "underpass flooded"],
}


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    return str(value).strip()


def lower_description(description: str) -> str:
    return normalize_text(description).lower()


def detect_category(description: str) -> str:
    """
    Map a complaint description to the allowed UC-0A category set.
    Warn when no category evidence is present by returning Other and letting
    the downstream flag handling label the row NEEDS_REVIEW.
    """
    text = lower_description(description)
    if not text:
        return "Other"

    # Prioritize high-confidence category words first.
    category_scores = {category: 0 for category in ALLOWED_CATEGORIES}
    evidence = []

    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                category_scores[category] += 1
                evidence.append(pattern)
                break

    # There are some descriptions that mention general words such as road or water.
    # Since the README requires a strict taxonomy, we prefer the most specific match.
    best_category = max(category_scores, key=lambda key: category_scores[key])
    if category_scores[best_category] == 0:
        return "Other"
    return best_category


def detect_priority(description: str) -> str:
    """
    Urgent if any severity keyword is present; otherwise choose Standard as the
    default neutral category. Low is allowed by the schema but not inferred here
    unless a future rule makes a low-risk issue explicit.
    """
    text = lower_description(description)
    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        return "Urgent"

    # Low-risk / non-urgent or mild descriptions default to Standard.
    # The README gives only one automatic trigger for Urgent; it does not
    # require a keyword trigger for Low. Standard is therefore the neutral fallback.
    return "Standard"


def make_reason(category: str, description: str, priority: str) -> str:
    """
    Return a one-sentence reason that cites words from the description.
    """
    text = normalize_text(description)
    text_lower = text.lower()

    evidence = []
    for category_name, patterns in CATEGORY_PATTERNS.items():
        if category == category_name:
            for pattern in patterns:
                if pattern in text_lower:
                    evidence.append(pattern)
                    break

    # If the category is Other and no evidence is available, explain that refusal.
    if category == "Other" or not evidence:
        reason = (
            f"The description does not provide enough evidence for a trusted category, "
            f"so category is Other and the row is flagged NEEDS_REVIEW."
        )
        return reason

    # Use the matched wording from the source description for an exact reason.
    # Use one sentence and maintain the README's justification requirements.
    cited = evidence[0]
    evidence_words = [word for word in re.findall(r"[A-Za-z]+", text) if word.lower() in text_lower]
    if evidence_words:
        cited = evidence_words[0]

    # If urgency words are present, mention them in the sentence.
    urgent_words_found = [keyword for keyword in SEVERITY_KEYWORDS if keyword in text_lower]
    urgent_text = ", ".join(urgent_words_found[:3]) if urgent_words_found else ""

    if priority == "Urgent" and urgent_text:
        return (
            f"The description mentions '{cited}' and the severity keywords '{urgent_text}', "
            f"so category is {category} and priority is Urgent."
        )

    return f"The description mentions '{cited}', so category is {category} and priority is {priority}."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    if not isinstance(row, dict):
        row = {}

    description = normalize_text(row.get("description", ""))
    complaint_id = normalize_text(row.get("complaint_id", ""))

    # Missing input is a soft failure: return a reviewable row instead of crashing.
    category = detect_category(description)
    priority = detect_priority(description)

    # If category cannot be determined from the description alone, refuse to guess.
    # README rules require category Other and NEEDS_REVIEW if category is genuinely ambiguous.
    # Since category detection is keyword-based, this path appears only when nothing matches.
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    # If the description has no category evidence at all, the row is genuinely ambiguous.
    if category == "Other" and description:
        flag = "NEEDS_REVIEW"

    # Merge category detection and flag policy.
    if not description.strip():
        category = "Other"
        flag = "NEEDS_REVIEW"

    reason = make_reason(category, description, priority)

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
    Produces output even on bad rows by writing Other + NEEDS_REVIEW.
    """
    input_dir = os.path.dirname(input_path)
    output_dir = os.path.dirname(output_path)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    input_rows = []
    try:
        with open(input_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            input_rows = list(reader)
    except Exception:
        # Ensure the tool never crashes on an unreadable or malformed input file.
        # Produce a header-only output file when no input can be read.
        with open(output_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
        return

    out_rows = []
    for row in input_rows:
        try:
            result = classify_complaint(row)
        except Exception:
            # If a row is malformed, return a safe review row.
            result = {
                "complaint_id": row.get("complaint_id", "") if isinstance(row, dict) else "",
                "category": "Other",
                "priority": "Standard",
                "reason": "The row could not be classified from the provided description, so category is Other and the row is flagged NEEDS_REVIEW.",
                "flag": "NEEDS_REVIEW",
            }
        out_rows.append(result)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in out_rows:
            # Ensure strict allowed fields.
            row = {
                "complaint_id": row.get("complaint_id", ""),
                "category": row.get("category", "Other") if row.get("category", "Other") in ALLOWED_CATEGORIES else "Other",
                "priority": row.get("priority", "Standard") if row.get("priority", "Standard") in {"Urgent", "Standard", "Low"} else "Standard",
                "reason": normalize_text(row.get("reason", "")),
                "flag": row.get("flag", "") if row.get("flag", "") in {"NEEDS_REVIEW", ""} else "",
            }
            # If category is other and no description evidence exists, flag review.
            if row["category"] == "Other" and row["flag"] != "NEEDS_REVIEW":
                row["flag"] = "NEEDS_REVIEW"
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "water logging", "waterlogged", "knee-deep"],
    "Streetlight": ["streetlight", "streetlights", "light out", "lights out", "flickering", "sparking", "dark at night"],
    "Waste": ["garbage", "trash", "waste", "bin", "dump", "overflowing garbage", "bulk waste"],
    "Noise": ["noise", "loud", "music past midnight", "honking", "playing music"],
    "Road Damage": ["road surface", "cracked", "sinking", "upturned", "broken tiles", "road damage", "road is", "depaved"],
    "Heritage Damage": ["heritage", "heritage street", "historic"],
    "Heat Hazard": ["heat", "hot", "heat hazard", "temperature"],
    "Drain Blockage": ["drain blocked", "drain blockage", "blocked drain", "drains clogged", "drain blocked"],
}

LOW_PRIORITY_KEYWORDS = ["minor", "small", "low priority", "not urgent", "low urgency"]


def _normalize(text: str) -> str:
    if text is None:
        return ""
    return text.strip().lower()


def _find_phrase(description: str, candidates: list[str]) -> str:
    lower = description.lower()
    for phrase in candidates:
        if phrase in lower:
            return phrase
    return ""


def classify_complaint(row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError("Row must be a dictionary")

    description = _normalize(row.get("description", ""))
    complaint_id = row.get("complaint_id", "")
    if description == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing, so category cannot be determined reliably.",
            "flag": "NEEDS_REVIEW",
        }

    # Priority enforcement
    priority = "Standard"
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            break

    if priority != "Urgent":
        for low_kw in LOW_PRIORITY_KEYWORDS:
            if low_kw in description:
                priority = "Low"
                break

    # Category classification with deterministic keyword scoring
    category_scores = {category: 0 for category in ALLOWED_CATEGORIES if category != "Other"}
    found_phrases: dict[str, list[str]] = {category: [] for category in category_scores}

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                if category in category_scores:
                    category_scores[category] += 1
                    found_phrases[category].append(keyword)

    # Choose best category
    best_category = "Other"
    best_score = 0
    for category, score in category_scores.items():
        if score > best_score:
            best_category = category
            best_score = score

    # Ambiguity detection
    ambiguity = False
    if best_score == 0:
        best_category = "Other"
        ambiguity = True
    else:
        sorted_scores = sorted(category_scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] == sorted_scores[1]:
            ambiguity = True

    reason_phrase = ""
    if best_category != "Other" and found_phrases.get(best_category):
        reason_phrase = found_phrases[best_category][0]
    else:
        # fallback phrase from description
        tokens = description.split(".")
        reason_phrase = tokens[0][:120].strip()
    if reason_phrase:
        reason = f"Description mentions \"{reason_phrase}\" which indicates {best_category.lower()}."
    else:
        reason = f"Complaint description indicates {best_category.lower()} based on provided text." 
    reason = reason.strip()
    if not reason.endswith("."):
        reason += "."

    flag = "NEEDS_REVIEW" if ambiguity else ""
    if best_category == "Other":
        flag = "NEEDS_REVIEW"

    # Enforce output enumerations
    if best_category not in ALLOWED_CATEGORIES:
        best_category = "Other"
        flag = "NEEDS_REVIEW"
    if priority not in ["Urgent", "Standard", "Low"]:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": best_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    classified = classify_complaint(row)
                    # Ensure all required keys exist
                    writer.writerow({k: classified.get(k, "") for k in output_fieldnames})
                except Exception:
                    writer.writerow(
                        {
                            "complaint_id": row.get("complaint_id", ""),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Error classifying this row; fell back to Other.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

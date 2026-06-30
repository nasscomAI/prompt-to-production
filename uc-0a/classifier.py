"""
UC-0A - Complaint Classifier
Production implementation following agents.md and skills.md specifications.
"""
import argparse
import csv
import sys
from pathlib import Path
from typing import Optional

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

OUTPUT_COLUMNS = ["complaint_id", "date_raised", "city", "ward", "location", "description", "category", "priority", "reason", "flag"]

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
    "Pothole": ["pothole", "hole", "crater", "pit", "damaged road", "pavement"],
    "Flooding": ["flood", "water", "inundation", "waterlog", "wet", "submerge"],
    "Streetlight": ["light", "lamp", "streetlight", "street light", "lighting", "bulb"],
    "Waste": ["garbage", "waste", "trash", "litter", "debris", "dump", "rubbish"],
    "Noise": ["noise", "loud", "sound", "honking", "music", "disturbance", "nuisance"],
    "Road Damage": ["crack", "damage", "erosion", "wear", "broken", "deteriorat"],
    "Heritage Damage": ["heritage", "monument", "historic", "ancient", "culture", "artifact"],
    "Heat Hazard": ["heat", "temperature", "hot", "sunburn", "exposure"],
    "Drain Blockage": ["drain", "blocked", "clogged", "sewage", "gutter", "canal", "blockage"],
}


def sanitize_input(text: Optional[str]) -> str:
    """Normalize and clean input text."""
    if not text:
        return ""
    return str(text).strip()


def has_severity_keywords(description: str) -> bool:
    """Check if description contains any severity trigger words."""
    description_lower = description.lower()
    return any(keyword in description_lower for keyword in SEVERITY_KEYWORDS)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input: dict with keys: complaint_id, description, latitude, longitude
    Output: dict with keys: complaint_id, category, priority, reason, flag
    """
    try:
        complaint_id = str(row.get("complaint_id", "")).strip()
        description = sanitize_input(row.get("description"))

        if not description:
            return {
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Standard",
                "reason": "No description provided.",
                "flag": "NEEDS_REVIEW",
            }

        description_lower = description.lower()
        scores = {}
        for category, keywords in CATEGORY_PATTERNS.items():
            score = sum(description_lower.count(keyword) for keyword in keywords)
            scores[category] = score

        max_score = max(scores.values()) if scores else 0
        top_categories = [category for category, score in scores.items() if score == max_score]

        if len(top_categories) > 1 and max_score > 0:
            selected_category = sorted(top_categories)[0]
            reason = f"Complaint mentions {len(top_categories)} possible categories; classified as '{selected_category}' based on keyword frequency."
            flag = "NEEDS_REVIEW"
        elif max_score == 0:
            selected_category = "Other"
            reason = "No clear category keywords detected in description."
            flag = "NEEDS_REVIEW"
        else:
            selected_category = top_categories[0]
            matched_keywords = [keyword for keyword in CATEGORY_PATTERNS[selected_category] if keyword in description_lower]
            if matched_keywords:
                cited_word = matched_keywords[0]
                reason = f"Complaint mentions '{cited_word}' which indicates {selected_category}."
            else:
                reason = f"Complaint classified as {selected_category}."
            flag = ""

        if has_severity_keywords(description):
            priority = "Urgent"
            if flag != "NEEDS_REVIEW":
                reason += " Contains severity keyword(s) indicating urgent priority."
        else:
            priority = "Standard"

        return {
            "complaint_id": complaint_id,
            "category": selected_category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception as exc:
        complaint_id = str(row.get("complaint_id", "unknown")).strip()
        print(f"ERROR classifying row {complaint_id}: {exc}", file=sys.stderr)
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classification failed due to processing error.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    error_count = 0
    success_count = 0

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                raise ValueError("Input CSV has no headers")

            for row_num, row in enumerate(reader, start=2):
                try:
                    classified = classify_complaint(row)
                    output_row = {
                        "complaint_id": row.get("complaint_id", ""),
                        "date_raised": row.get("date_raised", ""),
                        "city": row.get("city", ""),
                        "ward": row.get("ward", ""),
                        "location": row.get("location", ""),
                        "description": row.get("description", ""),
                        "category": classified.get("category", ""),
                        "priority": classified.get("priority", ""),
                        "reason": classified.get("reason", ""),
                        "flag": classified.get("flag", ""),
                    }
                    results.append(output_row)
                    success_count += 1
                except Exception as exc:
                    error_count += 1
                    complaint_id = str(row.get("complaint_id", f"row_{row_num}")).strip()
                    print(f"WARNING: Row {row_num} ({complaint_id}) failed to classify: {exc}", file=sys.stderr)
                    results.append(
                        {
                            "complaint_id": complaint_id,
                            "date_raised": row.get("date_raised", ""),
                            "city": row.get("city", ""),
                            "ward": row.get("ward", ""),
                            "location": row.get("location", ""),
                            "description": row.get("description", ""),
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Row processing failed.",
                            "flag": "NEEDS_REVIEW",
                        }
                    )

        if results:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                fieldnames = OUTPUT_COLUMNS
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            print(f"Classification complete: {success_count} succeeded, {error_count} failed", file=sys.stderr)
        else:
            raise ValueError("No rows were processed from input file")
    except FileNotFoundError:
        raise
    except Exception as exc:
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

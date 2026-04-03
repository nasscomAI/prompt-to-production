"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
# import argparse
# import csv

# def classify_complaint(row: dict) -> dict:
#     """
#     Classify a single complaint row.
#     Returns: dict with keys: complaint_id, category, priority, reason, flag
    
#     TODO: Build this using your AI tool guided by your agents.md and skills.md.
#     Your RICE enforcement rules must be reflected in this function's behaviour.
#     """
#     raise NotImplementedError("Build this using your AI tool + RICE prompt")


# def batch_classify(input_path: str, output_path: str):
#     """
#     Read input CSV, classify each row, write results CSV.
    
#     TODO: Build this using your AI tool.
#     Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
#     """
#     raise NotImplementedError("Build this using your AI tool + RICE prompt")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
#     parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
#     parser.add_argument("--output", required=True, help="Path to write results CSV")
#     args = parser.parse_args()
#     batch_classify(args.input, args.output)
#     print(f"Done. Results written to {args.output}")

import argparse
import csv

# Urgent severity keywords
URGENT_WORDS = [
    "injury", "injured", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse",
    "danger", "risk"
]


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # -------- CATEGORY RULES -------- #

    if "pothole" in description:
        category = "Pothole"
        reason = "Contains 'pothole'"

    elif "flood" in description or "rainwater" in description:
        category = "Flooding"
        reason = "Contains 'flood/rainwater'"

    elif "drain" in description or "blocked" in description or "sewage" in description:
        category = "Drain Blockage"
        reason = "Contains 'drain/blocked/sewage'"

    elif (
        "garbage" in description or
        "waste" in description or
        "overflow" in description or
        "dead animal" in description
    ):
        category = "Waste"
        reason = "Contains 'garbage/waste/overflow/dead animal'"

    elif (
        "streetlight" in description or
        "light" in description or
        "unlit" in description or
        "dark" in description or
        "wiring" in description
    ):
        category = "Streetlight"
        reason = "Contains 'light/unlit/dark/wiring'"

    elif (
        "noise" in description or
        "music" in description or
        "loud" in description or
        "drilling" in description or
        "idling" in description or 
        "band" in description or
        "playing" in description
    ):
        category = "Noise"
        reason = "Contains 'noise/music/loud/idling/band/playing'"

    elif (
        "broken" in description or
        "collapsed" in description or
        "collapse" in description or
        "crater" in description or
        "subsidence" in description or
        "subsided" in description or
        "buckled" in description or
        "cracked" in description or
        "sinking" in description or
        "manhole" in description or
        "fall risk" in description
    ):
        category = "Road Damage"
        reason = "Contains 'broken/collapsed/cracked/sinking/manhole/fall risk'"

    elif "heritage" in description:
        category = "Heritage Damage"
        reason = "Contains 'heritage'"

    elif (
        "heat" in description or
        "temperature" in description or
        "°c" in description or
        "melting" in description or
        "bubbling" in description or
        "hot" in description or
        "burn" in description
    ):
        category = "Heat Hazard"
        reason = "Contains 'heat/temperature/melting/bubbling'"

    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"No clear keyword match in: {description[:50]}"

    # -------- PRIORITY RULES -------- #

    if any(word in description for word in URGENT_WORDS):
        priority = "Urgent"
        if "urgent keyword" not in reason:
            reason += " and contains urgent keyword"
    else:
        priority = "Standard"

    # -------- RETURN -------- #

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")

"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "pit in road"],
    "Flooding": ["flood", "flooding", "waterlogging", "water logged", "inundated", "submerged", "rainwater"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "lights out", "unlit", "darkness", "dark"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "litter", "dump", "overflowing bin", "scattered waste", "dead animal"],
    "Noise": ["noise", "loud", "noisy", "disturbance", "honking", "blaring", "music", "drilling", "idling", "engines on", "amplifiers"],
    "Road Damage": ["road damage", "damaged road", "broken road", "crack in road", "cracks", "cracked", "sinking", "uneven road", "road repair", "manhole", "footpath", "tiles broken", "broken tiles", "collapsed", "crater", "buckled", "subsided", "cobblestones broken", "paving removed"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "protected structure", "vandalism on heritage", "heritage street", "heritage area", "heritage zone", "heritage stone", "heritage building", "heritage precinct"],
    "Heat Hazard": ["heat", "heatwave", "extreme heat", "sunstroke", "heat stroke", "hot weather", "melting", "temperatures", "bubbling", "unbearable", "sun"],
    "Drain Blockage": ["drain", "blocked drain", "clogged drain", "sewage", "overflowing drain", "stagnant water"]
}


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").lower().strip()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    if not description:
        flag = "NEEDS_REVIEW"
        reason = "Empty description provided"
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag
        }

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in description:
                category = cat
                break
        if category != "Other":
            break

    urgent_found = []
    for kw in SEVERITY_KEYWORDS:
        if kw in description:
            urgent_found.append(kw)

    if urgent_found:
        priority = "Urgent"

    matched_keywords = []
    if category != "Other":
        for kw in CATEGORY_KEYWORDS[category]:
            if kw in description:
                matched_keywords.append(kw)

    if matched_keywords:
        reason = f"Classified as {category} based on keywords: {', '.join(matched_keywords[:3])}"
    else:
        reason = f"No strong category keywords found; defaulting to {category}"

    if urgent_found:
        reason += f". Priority set to Urgent due to severity keywords: {', '.join(urgent_found)}"

    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", f"row_{i}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if not results:
        print("Warning: No results to write.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
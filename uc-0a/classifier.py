import argparse
import csv

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

URGENT_WORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").strip()
    text = description.lower()

    # Find category
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "flooding" in text:
        category = "Flooding"
    elif "streetlight" in text or "street light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text or "dumped" in text:
        category = "Waste"
    elif "noise" in text or "loud music" in text:
        category = "Noise"
    elif "road damage" in text or "cracked road" in text:
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text or "blocked drain" in text:
        category = "Drain Blockage"
    else:
        category = "Other"

    # Find urgent keywords
    urgent_word = next((word for word in URGENT_WORDS if word in text), None)

    priority = "Urgent" if urgent_word else "Standard"

    if urgent_word:
        reason = f"The description contains the severity keyword '{urgent_word}'."
    else:
        reason = f"The description indicates a {category.lower()} issue."

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": "The complaint could not be classified from the available description.",
                    "flag": "NEEDS_REVIEW",
                })

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        fields = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
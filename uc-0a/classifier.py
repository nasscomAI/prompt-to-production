import argparse
import csv

# Allowed categories
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    text = row.get("description", "")
    text_lower = text.lower()

    # ---------- Category ----------
    if "pothole" in text_lower:
        category = "Pothole"
    elif "flood" in text_lower or "waterlogging" in text_lower:
        category = "Flooding"
    elif "light" in text_lower:
        category = "Streetlight"
    elif "garbage" in text_lower or "waste" in text_lower:
        category = "Waste"
    elif "noise" in text_lower:
        category = "Noise"
    elif "road" in text_lower or "crack" in text_lower:
        category = "Road Damage"
    elif "heritage" in text_lower:
        category = "Heritage Damage"
    elif "heat" in text_lower:
        category = "Heat Hazard"
    elif "drain" in text_lower or "sewage" in text_lower:
        category = "Drain Blockage"
    else:
        category = "Other"

    # ---------- Priority ----------
    if any(word in text_lower for word in URGENT_KEYWORDS):
        priority = "Urgent"
    elif "danger" in text_lower or "severe" in text_lower:
        priority = "Standard"
    else:
        priority = "Low"

    # ---------- Reason (must cite words) ----------
    reason = f"Based on words: '{text[:40]}'"

    # ---------- Flag ----------
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception:
                    # Handle bad rows safely
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Row processing failed",
                        "flag": "NEEDS_REVIEW"
                    })

    except FileNotFoundError:
        print("Input file not found!")
        return

    # Write output
    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

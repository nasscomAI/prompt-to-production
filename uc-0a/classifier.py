"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Enforcement rule 1 -- see agents.md. Matched case-insensitively as substrings,
# which is what makes "child" catch "children" and "hazard" catch "hazards".
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority
    """
    text = row.get("description", "").lower()

    if "pothole" in text:
        category = "Potholes"
    elif "flood" in text or "water" in text:
        category = "Waterlogging"
    elif "streetlight" in text or "lights out" in text:
        category = "Street Light Issue"
    elif "garbage" in text or "waste" in text or "dumped" in text:
        category = "Garbage"
    elif "music" in text or "noise" in text:
        category = "Noise Complaint"
    elif "road" in text or "footpath" in text or "manhole" in text:
        category = "Road Maintenance"
    elif "animal" in text:
        category = "Sanitation"
    else:
        category = "General"

    # Enforcement: severity keywords force Urgent, checked before any other
    # priority logic. days_open is deliberately not consulted -- elapsed time is
    # a backlog metric, not a risk signal.
    if any(keyword in text for keyword in SEVERITY_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_complaint(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

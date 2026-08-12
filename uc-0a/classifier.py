"""
UC-0A — Complaint Classifier
NAIVE BASELINE (Control step) — mirrors what the naive prompt
"Classify this citizen complaint by category and priority." produces:
loose keyword guessing, no fixed taxonomy, no severity enforcement, no reason,
no flag. Kept here temporarily to document the Control run; see git history.
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    desc = (row.get("description") or "").lower()

    # Loose, unordered guessing -- first loose match wins, category strings
    # are whatever felt natural to write, not a fixed enum.
    if "pothole" in desc:
        category = "pothole"
    elif "flood" in desc:
        category = "Water Issue"
    elif "light" in desc:
        category = "Lighting"
    elif "garbage" in desc or "waste" in desc:
        category = "Sanitation"
    elif "noise" in desc or "music" in desc or "loud" in desc:
        category = "Noise Complaint"
    else:
        category = "General"

    # Priority guessed from days_open only -- no severity-keyword awareness.
    try:
        days_open = int(row.get("days_open") or 0)
    except ValueError:
        days_open = 0
    priority = "High" if days_open > 10 else "Normal"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [classify_complaint(row) for row in reader]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

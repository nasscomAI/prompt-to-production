import csv
import argparse
# minor fix
# final fix

# --- Simple rule-based classification (aligned with UC-0A intent) ---

def classify_complaint(text):
    text_lower = text.lower()

    # Category rules
    if any(word in text_lower for word in ["water", "leak", "pipeline"]):
        category = "Water Supply"
    elif any(word in text_lower for word in ["road", "pothole", "street"]):
        category = "Road Infrastructure"
    elif any(word in text_lower for word in ["garbage", "waste", "trash"]):
        category = "Sanitation"
    elif any(word in text_lower for word in ["electric", "power", "light"]):
        category = "Electricity"
    else:
        category = "Other"

    # Priority rules
    if any(word in text_lower for word in ["urgent", "immediately", "danger", "accident"]):
        priority_flag = "High"
    elif any(word in text_lower for word in ["delay", "pending", "long time"]):
        priority_flag = "Medium"
    else:
        priority_flag = "Low"

    # Justification (important for UC-0A)
    justification = f"Classified as {category} based on keywords; priority set to {priority_flag}."

    return category, priority_flag, justification


def batch_classify(input_file, output_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []

    for row in rows:
        complaint_text = row.get("complaint", "") or row.get("text", "")

        category, priority_flag, justification = classify_complaint(complaint_text)

        row["category"] = category
        row["priority_flag"] = priority_flag
        row["justification"] = justification

        output_rows.append(row)

    fieldnames = output_rows[0].keys()

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Classification complete. Output saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)
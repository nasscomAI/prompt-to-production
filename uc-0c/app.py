import argparse
import csv

REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes"
]

def load_dataset(input_path: str):
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    null_rows = []
    for row in rows:
        if str(row.get("actual_spend", "")).strip() == "":
            null_rows.append(row)

    return rows, null_rows

def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError("growth_type is required")

    if growth_type != "MoM":
        raise ValueError("Only MoM is implemented in this version")

    filtered = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    filtered.sort(key=lambda r: r["period"])

    output = []
    prev_value = None

    for row in filtered:
        actual_text = str(row["actual_spend"]).strip()
        period = row["period"]
        notes = row.get("notes", "").strip()

        if actual_text == "":
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "growth_value": "NOT_COMPUTED",
                "formula": "NULL actual_spend → growth not computed",
                "flag": f"NULL_ACTUAL_SPEND: {notes}"
            })
            prev_value = None
            continue

        current_value = float(actual_text)

        if prev_value is None:
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value}",
                "growth_type": growth_type,
                "growth_value": "N/A",
                "formula": "No previous month value available",
                "flag": ""
            })
        else:
            growth = ((current_value - prev_value) / prev_value) * 100
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{current_value}",
                "growth_type": growth_type,
                "growth_value": f"{growth:.1f}%",
                "formula": f"(({current_value} - {prev_value}) / {prev_value}) * 100",
                "flag": ""
            })

        prev_value = current_value

    return output

def write_output(output_path, rows):
    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "growth_type", "growth_value", "formula", "flag"
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, result)
    print(f"Done. Output written to {args.output}")
    print(f"Detected {len(null_rows)} null actual_spend rows in dataset.")

if __name__ == "__main__":
    main()
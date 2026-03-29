import argparse
import csv


REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes"
]


def load_dataset(input_path):
    data = []
    null_rows = []

    try:
        with open(input_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Validate columns
            for col in REQUIRED_COLUMNS:
                if col not in reader.fieldnames:
                    raise ValueError(f"Missing column: {col}")

            for row in reader:
                # Normalize
                row["actual_spend"] = row["actual_spend"].strip()

                if row["actual_spend"] == "":
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "reason": row["notes"]
                    })
                else:
                    row["actual_spend"] = float(row["actual_spend"])

                data.append(row)

    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
        exit()

    print(f"⚠️ Null rows detected: {len(null_rows)}")
    for r in null_rows:
        print(f"NULL → {r}")

    return data


def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        print("❌ growth-type must be specified")
        exit()

    if growth_type != "MoM":
        print("❌ Only MoM supported")
        exit()

    # Filter data
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_value = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"]

        if actual == "" or actual is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NA",
                "formula": "NA",
                "flag": f"NULL value → {row['notes']}"
            })
            prev_value = None
            continue

        if prev_value is None:
            results.append({
                "period": period,
                "actual_spend": actual,
                "growth": "NA",
                "formula": "No previous data",
                "flag": ""
            })
            prev_value = actual
            continue

        # Compute MoM growth
        growth = ((actual - prev_value) / prev_value) * 100

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth": f"{growth:.1f}%",
            "formula": f"(({actual} - {prev_value}) / {prev_value}) * 100",
            "flag": ""
        })

        prev_value = actual

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    # Write output
    with open(args.output, "w", newline='', encoding='utf-8') as file:
        fieldnames = ["period", "actual_spend", "growth", "formula", "flag"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Output written to {args.output}")


if __name__ == "__main__":
    main()
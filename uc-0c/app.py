import argparse
import csv


# ✅ Load dataset and detect null rows
def load_dataset(file_path):
    data = []
    null_rows = []

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        required_cols = ["period", "ward", "category", "actual_spend", "notes"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    return data, null_rows


# ✅ Compute Month-over-Month growth
def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Error: --growth-type must be specified")

    if growth_type != "MoM":
        raise ValueError("Error: Only MoM growth supported")

    # 🔹 Filter by ward + category (NO aggregation)
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    # 🔹 Sort by month
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for row in filtered:
        period = row["period"]
        spend = row["actual_spend"]

        # 🔴 Handle NULL values
        if spend == "" or spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": f"NULL (Reason: {row['notes']})"
            })
            prev = None
            continue

        spend = float(spend)

        # First valid row
        if prev is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "No previous value"
            })
        else:
            growth = ((spend - prev) / prev) * 100
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": f"{growth:.1f}%",
                "formula": f"(({spend} - {prev}) / {prev}) * 100"
            })

        prev = spend

    return results


# ✅ Write output CSV
def write_output(output_path, results):
    with open(output_path, 'w', newline='') as file:
        fieldnames = ["period", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


# ✅ Main function
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    # Load data
    data, null_rows = load_dataset(args.input)

    # 🔥 Print all null rows BEFORE computation
    print("Null rows detected:")
    for r in null_rows:
        print(f"{r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")

    # Compute growth
    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    # Save output
    write_output(args.output, results)

    print("Growth output generated successfully.")


if __name__ == "__main__":
    main()
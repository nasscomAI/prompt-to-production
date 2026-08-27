import argparse
import csv

def load_dataset(path):
    data = []
    null_rows = []

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["actual_spend"] == "" or row["actual_spend"] is None:
                null_rows.append(row)
            data.append(row)

    return data, null_rows


def compute_growth(data, ward, category):
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]

    filtered.sort(key=lambda x: x["period"])

    output = []
    prev = None

    for row in filtered:
        spend = row["actual_spend"]

        if spend == "" or spend is None:
            output.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "Not computed"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            output.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth": "NA",
                "formula": "First period"
            })
        else:
            growth = ((spend - prev) / prev) * 100
            formula = f"({spend}-{prev})/{prev}*100"
            output.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": spend,
                "growth": round(growth, 2),
                "formula": formula
            })

        prev = spend

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data, null_rows = load_dataset(args.input)

    results = compute_growth(data, args.ward, args.category)

    with open(args.output, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"]
        )
        writer.writeheader()
        writer.writerows(results)

    print("Growth output generated.")


if __name__ == "__main__":
    main()
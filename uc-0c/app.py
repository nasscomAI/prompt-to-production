import argparse
import csv


def load_dataset(file_path):

    data = []

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data.append(row)

    return data


def compute_growth(data, ward, category, growth_type):

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]

    filtered.sort(key=lambda x: x["period"])

    results = []

    prev_spend = None

    for row in filtered:

        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]

        if spend == "" or spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL VALUE – growth not computed",
                "notes": notes
            })
            prev_spend = None
            continue

        spend = float(spend)

        if prev_spend is None:
            growth = "N/A"
            formula = "First period – no previous value"
        else:
            growth_val = ((spend - prev_spend) / prev_spend) * 100
            growth = f"{growth_val:.2f}%"
            formula = f"(({spend}-{prev_spend})/{prev_spend})*100"

        results.append({
            "period": period,
            "actual_spend": spend,
            "growth": growth,
            "formula": formula,
            "notes": notes
        })

        prev_spend = spend

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(data, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["period", "actual_spend", "growth", "formula", "notes"]
        )

        writer.writeheader()
        writer.writerows(results)

    print("Growth analysis completed.")


if __name__ == "__main__":
    main()
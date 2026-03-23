import argparse
import csv


def load_dataset(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

        for col in required:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        for row in reader:
            rows.append(row)

    return rows


def compute_growth(rows, ward, category, growth_type):

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for r in filtered:
        period = r["period"]
        spend = r["actual_spend"]

        if not spend:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "NULL value flagged"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": "N/A",
                "formula": "No previous period"
            })
        else:
            growth = ((spend - prev) / prev) * 100
            formula = f"(({spend}-{prev})/{prev})*100"

            results.append({
                "period": period,
                "actual_spend": spend,
                "growth": round(growth, 2),
                "formula": formula
            })

        prev = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Only MoM growth supported for this task")

    rows = load_dataset(args.input)

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
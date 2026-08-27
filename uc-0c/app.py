import argparse
import csv


def load_dataset(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def compute_growth(rows, ward, category, growth_type):
    filtered = []

    for r in rows:
        if r["ward"] == ward and r["category"] == category:
            filtered.append(r)

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for row in filtered:
        spend = row["actual_spend"]

        if spend == "" or spend is None:
            results.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": "FLAGGED_NULL",
                "formula": "N/A",
                "notes": row["notes"]
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            growth = "N/A"
            formula = "N/A"
        else:
            if growth_type == "MoM":
                value = ((spend - prev) / prev) * 100
                growth = f"{value:.2f}%"
                formula = "(current - previous) / previous * 100"
            else:
                raise ValueError("Unsupported growth type")

        results.append({
            "period": row["period"],
            "actual_spend": spend,
            "growth": growth,
            "formula": formula,
            "notes": row["notes"]
        })

        prev = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period", "actual_spend", "growth", "formula", "notes"]
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth results written to {args.output}")


if __name__ == "__main__":
    main()
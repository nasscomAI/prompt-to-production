import argparse
import csv

def load_dataset(file_path):
    rows = []
    null_rows = []

    with open(file_path) as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["actual_spend"] == "":
                null_rows.append(row)
            rows.append(row)

    return rows, null_rows


def compute_growth(data, ward, category):
    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []

    prev = None
    for row in filtered:
        period = row["period"]
        spend = row["actual_spend"]

        if spend == "":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "FLAG_NULL",
                "formula": "actual_spend missing"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            growth = "N/A"
            formula = "first period"
        else:
            growth_val = ((spend - prev) / prev) * 100
            growth = f"{growth_val:.1f}%"
            formula = f"(({spend}-{prev})/{prev})*100"

        results.append({
            "period": period,
            "actual_spend": spend,
            "growth": growth,
            "formula": formula
        })

        prev = spend

    return results


def write_output(rows, output_file):
    with open(output_file, "w", newline="") as f:
        fieldnames = ["period", "actual_spend", "growth", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data, null_rows = load_dataset(args.input)

    print("Null rows detected:", len(null_rows))

    results = compute_growth(data, args.ward, args.category)

    write_output(results, args.output)

    print("Growth output written to", args.output)


if __name__ == "__main__":
    main()

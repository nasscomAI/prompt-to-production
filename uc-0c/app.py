import argparse
import csv

def calculate_growth(data):
    results = []
    prev = None

    for row in data:
        current = float(row["actual_spend"])
        period = row["period"]

        if prev is None:
            growth = "N/A"
        else:
            growth = ((current - prev) / prev) * 100

        results.append({
            "period": period,
            "actual_spend": current,
            "growth_value": growth
        })

        prev = current

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    filtered = []

    with open(args.input) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["ward"] == args.ward and row["category"] == args.category:
                filtered.append(row)

    results = calculate_growth(filtered)

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["period","actual_spend","growth_value"])
        writer.writeheader()
        writer.writerows(results)

    print("Growth results written to", args.output)


if __name__ == "__main__":
    main()
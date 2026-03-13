import argparse
import csv


def load_dataset(path):

    rows = []
    null_rows = []

    with open(path, newline='') as f:
        reader = csv.DictReader(f)

        for row in reader:

            if row["actual_spend"] == "" or row["actual_spend"] is None:
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
                "growth": "NULL",
                "formula": "actual_spend missing → growth not computed"
            })
            prev = None
            continue

        spend = float(spend)

        if prev is None:
            results.append({
                "period": period,
                "growth": "N/A",
                "formula": "first period"
            })
        else:
            growth = ((spend - prev) / prev) * 100
            results.append({
                "period": period,
                "growth": f"{growth:.2f}%",
                "formula": f"(({spend}-{prev})/{prev})*100"
            })

        prev = spend

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type != "MoM":
        raise ValueError("Only MoM growth supported")

    data, null_rows = load_dataset(args.input)

    if null_rows:
        print("Null rows detected:")
        for r in null_rows:
            print(r["period"], r["ward"], r["category"])

    results = compute_growth(data, args.ward, args.category)

    with open(args.output, "w", newline="") as f:

        writer = csv.DictWriter(f, fieldnames=["period", "growth", "formula"])

        writer.writeheader()

        for r in results:
            writer.writerow(r)

    print("Growth output written to", args.output)


if __name__ == "__main__":
    main()
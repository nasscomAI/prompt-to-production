import argparse
import csv


def load_dataset(path):

    rows = []

    with open(path, newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for r in reader:
            rows.append(r)

    return rows


def compute_growth(rows, ward, category):

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for r in filtered:

        period = r["period"]
        actual = r["actual_spend"]
        note = r["notes"]

        if actual == "" or actual is None:

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_percent": "NULL",
                "formula": "NULL",
                "flag": f"NULL actual_spend — {note}"
            })

            prev = None
            continue

        actual = float(actual)

        if prev is None:

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth_percent": "N/A",
                "formula": "First period — no previous value",
                "flag": ""
            })

        else:

            growth = ((actual - prev) / prev) * 100

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "growth_percent": round(growth, 2),
                "formula": f"(({actual}-{prev})/{prev})*100",
                "flag": ""
            })

        prev = actual

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
        raise Exception("Only MoM growth supported")

    rows = load_dataset(args.input)

    results = compute_growth(rows, args.ward, args.category)

    with open(args.output, "w", newline="", encoding="utf-8") as f:

        fieldnames = [
            "period",
            "ward",
            "category",
            "actual_spend",
            "growth_percent",
            "formula",
            "flag"
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for r in results:
            writer.writerow(r)

    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()
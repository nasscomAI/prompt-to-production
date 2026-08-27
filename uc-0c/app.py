import argparse
import csv

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes"
]


def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for column in REQUIRED_COLUMNS:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing required column: {column}")

        return list(reader)


def compute_growth(data, ward, category, growth_type):

    if growth_type is None:
        raise ValueError("Growth type is required.")

    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    results = []

    previous = None

    for row in filtered:

        spend = row["actual_spend"]

        if spend == "":
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "growth": "",
                "formula": "Not computed",
                "flag": f"NULL VALUE - {row['notes']}"
            })
            continue

        spend = float(spend)

        if previous is None:
            growth = ""
            formula = "First Period"
        else:
            growth = round(((spend - previous) / previous) * 100, 2)
            formula = "((Current-Previous)/Previous)*100"

        results.append({
            "period": row["period"],
            "ward": ward,
            "category": category,
            "growth": growth,
            "formula": formula,
            "flag": ""
        })

        previous = spend

    return results


def main():

    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    output = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "period",
                "ward",
                "category",
                "growth",
                "formula",
                "flag"
            ]
        )

        writer.writeheader()
        writer.writerows(output)

    print(f"Growth report saved to {args.output}")


if __name__ == "__main__":
    main()

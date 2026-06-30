"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


def load_dataset(input_file):
    rows = []

    required_columns = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes"
    ]

    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing column: {column}")

        for row in reader:
            rows.append(row)

    return rows


def compute_growth(data, ward, category, growth_type):

    if not growth_type:
        raise ValueError("Growth type must be specified.")

    filtered = []

    for row in data:

        if row["ward"] != ward:
            continue

        if row["category"] != category:
            continue

        if row["actual_spend"] == "":
            filtered.append({
                "period": row["period"],
                "actual_spend": "",
                "growth": "",
                "formula": "",
                "status": "NULL VALUE",
                "notes": row["notes"]
            })
            continue

        filtered.append({
            "period": row["period"],
            "actual_spend": row["actual_spend"],
            "growth": "",
            "formula": "(Current-Previous)/Previous*100",
            "status": "OK",
            "notes": row["notes"]
        })

    previous = None

    for row in filtered:

        if row["status"] != "OK":
            continue

        current = float(row["actual_spend"])

        if previous is None:
            row["growth"] = ""
        else:
            row["growth"] = round(((current - previous) / previous) * 100, 2)

        previous = current

    return filtered


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", newline="", encoding="utf-8") as file:

        fields = [
            "period",
            "actual_spend",
            "growth",
            "formula",
            "status",
            "notes"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

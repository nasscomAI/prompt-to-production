import argparse
import csv


def load_dataset(input_file):
    with open(input_file, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("Dataset is empty.")

    required = {
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes"
    }

    if not required.issubset(rows[0].keys()):
        raise ValueError("Required columns are missing.")

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not ward:
        raise ValueError("Ward must be specified.")

    if not category:
        raise ValueError("Category must be specified.")

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Use --growth-type MoM."
        )

    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. Only MoM is supported."
        )

    if ward.upper() == "ALL":
        raise ValueError(
            "Refused: all-ward aggregation is not allowed. "
            "Specify exactly one ward."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            "No data found for the specified ward and category."
        )

    selected.sort(key=lambda row: row["period"])

    output = []
    previous = None

    for row in selected:
        spend = row["actual_spend"].strip()

        # Null actual spend must never be used in calculation.
        if spend == "":
            output.append({
                "period": row["period"],
                "actual_spend": "",
                "formula": "NOT COMPUTED",
                "growth": "NULL",
                "status": "FLAGGED: " + row["notes"]
            })

            # Reset previous value so the next available value
            # does not calculate growth against the missing value.
            previous = None
            continue

        current = float(spend)

        if previous is None:
            formula = "N/A (first available period)"
            growth = ""
        else:
            growth_value = ((current - previous) / previous) * 100
            growth = f"{growth_value:+.1f}%"
            formula = (
                f"(({current} - {previous}) / "
                f"{previous}) * 100"
            )

        output.append({
            "period": row["period"],
            "actual_spend": spend,
            "formula": formula,
            "growth": growth,
            "status": ""
        })

        previous = current

    return output


def write_output(output, output_file):
    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        fieldnames = [
            "period",
            "actual_spend",
            "formula",
            "growth",
            "status"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(output)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Analysis"
    )

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--ward",
        required=True
    )

    parser.add_argument(
        "--category",
        required=True
    )

    parser.add_argument(
        "--growth-type",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    output = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(output, args.output)

    print(
        f"Growth results written to {args.output}"
    )


if __name__ == "__main__":
    main()
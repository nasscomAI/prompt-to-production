"""""
UC-0C - Number That Looks Right
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    path = Path(input_path)

    if not path.exists():
        raise ValueError(f"Input file does not exist: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        return list(reader)


def is_missing(value):
    if value is None:
        return True

    value = str(value).strip()

    return value == "" or value.upper() == "NULL"


def parse_spend(value):
    if is_missing(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def period_key(period):
    year, month = str(period).strip().split("-")
    return int(year), int(month)


def compute_mom(rows):
    """
    Compute month-over-month growth separately for each
    ward + category combination.
    """

    groups = defaultdict(list)

    for row in rows:
        key = (row["ward"], row["category"])
        groups[key].append(row)

    results = []

    for (ward, category), group in groups.items():

        group.sort(key=lambda row: period_key(row["period"]))

        previous_period = None
        previous_value = None

        for row in group:

            current_value = parse_spend(row["actual_spend"])

            # NULL / invalid actual spend
            if current_value is None:

                results.append({
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": row["actual_spend"],
                    "comparison_period": "",
                    "comparison_actual_spend": "",
                    "growth_type": "MoM",
                    "formula": "",
                    "growth": "",
                    "status": "FLAGGED_NULL",
                    "reason": row["notes"]
                    or "actual_spend is NULL or invalid",
                })

                # Do NOT use a NULL row as a comparison point.
                previous_period = None
                previous_value = None

                continue

            # First valid observation
            if previous_value is None:

                results.append({
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": f"{current_value:.1f}",
                    "comparison_period": "",
                    "comparison_actual_spend": "",
                    "growth_type": "MoM",
                    "formula": "",
                    "growth": "",
                    "status": "NO_COMPARISON",
                    "reason": (
                        "No valid previous period available "
                        "within the same ward/category."
                    ),
                })

            # Previous value is zero
            elif previous_value == 0:

                results.append({
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": f"{current_value:.1f}",
                    "comparison_period": previous_period,
                    "comparison_actual_spend": f"{previous_value:.1f}",
                    "growth_type": "MoM",
                    "formula": (
                        "((current - previous) / previous) × 100"
                    ),
                    "growth": "",
                    "status": "FLAGGED_ZERO_BASE",
                    "reason": (
                        "Previous actual_spend is zero; "
                        "percentage growth is undefined."
                    ),
                })

            else:

                growth = (
                    (current_value - previous_value)
                    / previous_value
                    * 100
                )

                formula = (
                    f"(({current_value:.1f} - "
                    f"{previous_value:.1f}) / "
                    f"{previous_value:.1f}) × 100 = "
                    f"{growth:+.1f}%"
                )

                results.append({
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": f"{current_value:.1f}",
                    "comparison_period": previous_period,
                    "comparison_actual_spend":
                        f"{previous_value:.1f}",
                    "growth_type": "MoM",
                    "formula": formula,
                    "growth": f"{growth:+.1f}%",
                    "status": "CALCULATED",
                    "reason": "",
                })

            previous_period = row["period"]
            previous_value = current_value

    return results


def write_output(output_path, results):

    fields = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "comparison_period",
        "comparison_actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "reason",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(results)


def main():

    parser = argparse.ArgumentParser(
        description="UC-0C ward/category growth calculator"
    )

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    parser.add_argument(
        "--growth-type",
        choices=["mom"],
        help="Required. Currently supported: mom"
    )

    args = parser.parse_args()

    # Explicit refusal when growth type is missing.
    if not args.growth_type:

        print(
            "REFUSED: --growth-type is required. "
            "Specify --growth-type mom.",
            file=sys.stderr
        )

        return 2

    try:

        rows = load_dataset(args.input)

        results = compute_mom(rows)

        write_output(
            args.output,
            results
        )

        null_count = sum(
            r["status"] == "FLAGGED_NULL"
            for r in results
        )

        calculated_count = sum(
            r["status"] == "CALCULATED"
            for r in results
        )

        print(f"Loaded rows: {len(rows)}")
        print(
            f"Calculated growth rows: "
            f"{calculated_count}"
        )
        print(
            f"Flagged NULL rows: "
            f"{null_count}"
        )
        print(
            f"Output written to: "
            f"{args.output}"
        )

        return 0

    except ValueError as exc:

        print(
            f"REFUSED: {exc}",
            file=sys.stderr
        )

        return 2


if __name__ == "__main__":
    raise SystemExit(main())
"""
UC-0C — Budget Growth Calculator
"""

import argparse
import csv


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    """Load CSV, validate columns, and report null actual_spend rows."""

    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = [
        row for row in rows
        if not (row.get("actual_spend") or "").strip()
    ]

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute monthly growth for exactly one ward and one category."""

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly specified; refusing to guess."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "Only MoM is supported."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No records found for ward='{ward}' "
            f"and category='{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []
    previous = None

    for row in selected:
        current_text = (row.get("actual_spend") or "").strip()

        # First period has no previous month.
        if previous is None:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": current_text or "NULL",
                "previous_actual_spend": "N/A",
                "growth_type": "MoM",
                "formula": "N/A — no previous month",
                "growth": "N/A",
                "status": "BASE_PERIOD",
                "null_reason": (
                    row.get("notes", "")
                    if not current_text else ""
                ),
            })

            previous = row
            continue

        previous_text = (previous.get("actual_spend") or "").strip()

        # Current value is NULL.
        if not current_text:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "previous_actual_spend": previous_text or "NULL",
                "growth_type": "MoM",
                "formula": (
                    "NOT COMPUTED — current actual_spend is NULL"
                ),
                "growth": "N/A",
                "status": "NULL_CURRENT",
                "null_reason": (
                    row.get("notes", "") or "No reason provided"
                ),
            })

            previous = row
            continue

        # Previous value is NULL.
        if not previous_text:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": current_text,
                "previous_actual_spend": "NULL",
                "growth_type": "MoM",
                "formula": (
                    "NOT COMPUTED — previous actual_spend is NULL"
                ),
                "growth": "N/A",
                "status": "NULL_PREVIOUS",
                "null_reason": (
                    previous.get("notes", "")
                    or "No reason provided"
                ),
            })

            previous = row
            continue

        current = float(current_text)
        previous_value = float(previous_text)

        if previous_value == 0:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": current_text,
                "previous_actual_spend": previous_text,
                "growth_type": "MoM",
                "formula": (
                    "NOT COMPUTED — previous actual_spend is zero"
                ),
                "growth": "N/A",
                "status": "ZERO_PREVIOUS",
                "null_reason": "",
            })

            previous = row
            continue

        growth = (
            (current - previous_value)
            / previous_value
        ) * 100

        formula = (
            f"(({current:.1f} - {previous_value:.1f}) "
            f"/ {previous_value:.1f}) * 100"
        )

        results.append({
            "period": row["period"],
            "ward": ward,
            "category": category,
            "actual_spend": f"{current:.1f}",
            "previous_actual_spend": f"{previous_value:.1f}",
            "growth_type": "MoM",
            "formula": formula,
            "growth": f"{growth:+.1f}%",
            "status": "COMPUTED",
            "null_reason": "",
        })

        previous = row

    return results


def write_output(output_path, results):
    """Write per-period results to CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "previous_actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Dataset loaded: {len(rows)} rows.")
    print(f"Null actual_spend rows detected: {len(null_rows)}.")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"Reason: {row.get('notes', '')}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
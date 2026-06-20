"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path: str) -> dict:
    """Read the dataset, validate required columns, and report null rows."""
    with Path(input_path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Dataset is missing a header row.")

        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

        rows = []
        null_rows = []
        wards = set()
        categories = set()

        for row in reader:
            parsed_row = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"]),
                "actual_spend": None if row["actual_spend"].strip() == "" else float(row["actual_spend"]),
                "notes": row["notes"].strip(),
            }
            rows.append(parsed_row)
            wards.add(parsed_row["ward"])
            categories.add(parsed_row["category"])
            if parsed_row["actual_spend"] is None:
                null_rows.append(parsed_row)

    return {
        "rows": rows,
        "wards": sorted(wards),
        "categories": sorted(categories),
        "null_rows": null_rows,
        "null_count": len(null_rows),
    }


def _find_comparison_row(rows: list[dict], index: int, growth_type: str) -> dict | None:
    if growth_type == "MoM":
        return rows[index - 1] if index > 0 else None
    if growth_type == "YoY":
        current_period = rows[index]["period"]
        target_year = str(int(current_period[:4]) - 1)
        target_period = f"{target_year}{current_period[4:]}"
        for row in rows:
            if row["period"] == target_period:
                return row
        return None
    raise ValueError(f"Unsupported growth type: {growth_type}")


def _format_percent(value: float) -> str:
    return f"{value:+.1f}%"


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list[dict]:
    """Return per-period growth rows for exactly one ward and one category."""
    if not ward or ward.upper() == "ALL":
        raise ValueError("Refused: ward must be specified explicitly; all-ward aggregation is not allowed.")
    if not category or category.upper() == "ALL":
        raise ValueError("Refused: category must be specified explicitly; all-category aggregation is not allowed.")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Refused: growth_type must be specified as MoM or YoY.")

    filtered_rows = [
        row for row in dataset["rows"] if row["ward"] == ward and row["category"] == category
    ]
    if not filtered_rows:
        raise ValueError("No rows matched the requested ward and category.")

    filtered_rows.sort(key=lambda row: row["period"])
    output_rows = []

    for index, row in enumerate(filtered_rows):
        comparison_row = _find_comparison_row(filtered_rows, index, growth_type)
        formula_template = "((current_actual_spend - comparison_actual_spend) / comparison_actual_spend) * 100"
        output = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": f"{row['budgeted_amount']:.1f}",
            "actual_spend": "" if row["actual_spend"] is None else f"{row['actual_spend']:.1f}",
            "comparison_period": "" if comparison_row is None else comparison_row["period"],
            "comparison_actual_spend": "" if comparison_row is None or comparison_row["actual_spend"] is None else f"{comparison_row['actual_spend']:.1f}",
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": formula_template,
            "status": "",
            "notes": row["notes"],
        }

        if row["actual_spend"] is None:
            output["status"] = "FLAGGED_NULL"
            if row["notes"]:
                output["notes"] = row["notes"]
            output["formula"] = formula_template + " ; not computed because current actual_spend is null"
            output_rows.append(output)
            continue

        if comparison_row is None:
            output["status"] = "NO_BASELINE"
            output["formula"] = formula_template + f" ; not computed because no {growth_type} comparison period exists"
            output_rows.append(output)
            continue

        if comparison_row["actual_spend"] is None:
            output["status"] = "PREVIOUS_NULL"
            if comparison_row["notes"]:
                output["notes"] = comparison_row["notes"]
            output["formula"] = formula_template + " ; not computed because comparison actual_spend is null"
            output_rows.append(output)
            continue

        if comparison_row["actual_spend"] == 0:
            output["status"] = "ZERO_BASE"
            output["formula"] = formula_template + " ; not computed because comparison actual_spend is zero"
            output_rows.append(output)
            continue

        growth_value = ((row["actual_spend"] - comparison_row["actual_spend"]) / comparison_row["actual_spend"]) * 100
        output["growth_percent"] = _format_percent(growth_value)
        output["status"] = "COMPUTED"
        output["formula"] = (
            f"(({row['actual_spend']:.1f} - {comparison_row['actual_spend']:.1f}) / "
            f"{comparison_row['actual_spend']:.1f}) * 100 = {output['growth_percent']}"
        )
        output_rows.append(output)

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth calculation type")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)

    output_fields = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "comparison_period",
        "comparison_actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "notes",
    ]
    with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(growth_rows)

    print(f"Loaded {len(dataset['rows'])} rows; flagged {dataset['null_count']} null actual_spend rows.")
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

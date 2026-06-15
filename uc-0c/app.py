"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
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


def load_dataset(input_path: str) -> list[dict]:
    with open(input_path, "r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - fieldnames
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

        rows = list(reader)

    null_rows = [
        row for row in rows if not (row.get("actual_spend") or "").strip()
    ]
    if len(null_rows) != 5:
        raise ValueError(f"Expected 5 null actual_spend rows, found {len(null_rows)}")

    return rows


def _parse_amount(value: str) -> float | None:
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return float(cleaned)


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("--growth-type must be either 'MoM' or 'YoY'")

    filtered_rows = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]
    if not filtered_rows:
        raise ValueError("No rows found for the requested ward and category")

    filtered_rows.sort(key=lambda row: row["period"])
    output_rows = []

    for index, row in enumerate(filtered_rows):
        period = row["period"]
        actual_spend = _parse_amount(row["actual_spend"])
        notes = (row.get("notes") or "").strip()

        result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "" if actual_spend is None else f"{actual_spend:.1f}",
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": "",
            "status": "OK",
            "notes": notes,
        }

        if actual_spend is None:
            result["status"] = "NULL_ACTUAL"
            result["formula"] = "Not computed because actual_spend is NULL"
            output_rows.append(result)
            continue

        offset = 1 if growth_type == "MoM" else 12
        if index < offset:
            result["status"] = "BASE_PERIOD"
            result["formula"] = f"No {growth_type} comparison period available"
            output_rows.append(result)
            continue

        previous_row = filtered_rows[index - offset]
        previous_spend = _parse_amount(previous_row["actual_spend"])
        if previous_spend is None:
            result["status"] = "PREVIOUS_NULL"
            result["formula"] = (
                f"Not computed because comparison period {previous_row['period']} has NULL actual_spend"
            )
            if notes:
                result["notes"] = notes
            output_rows.append(result)
            continue

        if previous_spend == 0:
            result["status"] = "PREVIOUS_ZERO"
            result["formula"] = (
                f"Not computed because comparison period {previous_row['period']} actual_spend is 0"
            )
            output_rows.append(result)
            continue

        growth = ((actual_spend - previous_spend) / previous_spend) * 100
        result["growth_percent"] = f"{growth:+.1f}%"
        result["formula"] = (
            f"(({actual_spend:.1f} - {previous_spend:.1f}) / {previous_spend:.1f}) * 100"
        )
        output_rows.append(result)

    return output_rows


def write_output(output_path: str, rows: list[dict]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "notes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth comparison to compute: MoM or YoY",
    )
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    if args.ward.strip().lower() in {"all", "*"} or args.category.strip().lower() in {"all", "*"}:
        raise ValueError("Refusing all-ward or all-category aggregation; provide one exact ward and one exact category")

    dataset = load_dataset(args.input)
    growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    write_output(args.output, growth_rows)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()

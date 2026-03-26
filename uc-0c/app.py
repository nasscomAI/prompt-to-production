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


def _to_float(value: str):
    value = (value or "").strip()
    if value == "":
        return None
    return float(value)


def load_dataset(input_path: str) -> tuple:
    """
    Read and validate dataset, returning all rows and null-row report.
    """
    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header")

        columns = {name.strip() for name in reader.fieldnames}
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows = []
        null_rows = []
        for row in reader:
            normalized = {
                "period": (row.get("period") or "").strip(),
                "ward": (row.get("ward") or "").strip(),
                "category": (row.get("category") or "").strip(),
                "budgeted_amount": _to_float(row.get("budgeted_amount") or ""),
                "actual_spend": _to_float(row.get("actual_spend") or ""),
                "notes": (row.get("notes") or "").strip(),
            }
            rows.append(normalized)
            if normalized["actual_spend"] is None:
                null_rows.append(normalized)

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute period-wise growth for one ward and one category only.
    """
    if not ward or not category:
        raise ValueError("Ward and category must both be provided; cross-ward/category aggregation is not allowed")
    if not growth_type:
        raise ValueError("--growth-type is required. Refusing to guess between MoM and YoY")

    growth_type_normalized = growth_type.strip().upper()
    if growth_type_normalized not in {"MOM", "YOY"}:
        raise ValueError("Unsupported growth type. Allowed values: MoM, YoY")

    scoped = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]
    if not scoped:
        raise ValueError("No rows found for the provided ward/category")

    scoped.sort(key=lambda item: item["period"])
    index_by_period = {row["period"]: row for row in scoped}

    result = []
    for row in scoped:
        period = row["period"]
        current = row["actual_spend"]
        status = "OK"
        null_reason = ""
        formula = ""
        growth_percent = ""

        if current is None:
            status = "NULL_FLAGGED"
            null_reason = row["notes"] or "Null actual_spend with no note"
            formula = "Not computed due to null actual_spend"
        else:
            if growth_type_normalized == "MOM":
                year, month = period.split("-")
                previous_period = f"{year}-{int(month) - 1:02d}" if month != "01" else ""
            else:
                year, month = period.split("-")
                previous_period = f"{int(year) - 1}-{month}"

            previous = index_by_period.get(previous_period) if previous_period else None
            prev_value = None if previous is None else previous["actual_spend"]

            if previous is None:
                status = "NO_BASE_PERIOD"
                formula = f"{growth_type_normalized}: base period unavailable"
            elif prev_value is None:
                status = "NO_BASE_VALUE"
                null_reason = previous.get("notes", "") or f"Base period {previous_period} has null actual_spend"
                formula = f"{growth_type_normalized}: base period {previous_period} has null actual_spend"
            elif prev_value == 0:
                status = "NO_BASE_VALUE"
                formula = f"{growth_type_normalized}: cannot divide by zero (base period {previous_period} = 0)"
            else:
                delta = ((current - prev_value) / prev_value) * 100.0
                growth_percent = f"{delta:.1f}"
                formula = f"(({current:.1f} - {prev_value:.1f}) / {prev_value:.1f}) * 100"

        result.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "" if current is None else f"{current:.1f}",
                "growth_type": growth_type_normalized,
                "growth_percent": growth_percent,
                "formula": formula,
                "status": status,
                "null_reason": null_reason,
            }
        )

    return result


def write_growth_output(output_path: str, rows: list):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "null_reason",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_growth_output(args.output, output_rows)

    print(f"Done. Growth output written to {args.output}")
    print(f"Null rows detected in dataset: {len(null_rows)}")
    for null_row in null_rows:
        print(
            f"NULL -> period={null_row['period']}, ward={null_row['ward']}, "
            f"category={null_row['category']}, note={null_row['notes'] or 'N/A'}"
        )

if __name__ == "__main__":
    main()

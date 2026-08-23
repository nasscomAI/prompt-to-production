"""UC-0C — Per-ward, per-category budget growth calculator."""

import argparse
import csv

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """Load, validate, and report null actual-spend rows."""
    with open(input_path, newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    null_rows = [row for row in rows if not str(row["actual_spend"]).strip()]
    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """Compute growth without crossing missing values."""
    if not ward.strip() or not category.strip():
        raise ValueError("Both ward and category are required.")
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError("growth_type must be explicitly specified as MoM or YoY.")

    selected = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]
    selected.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in selected}
    results = []
    for index, row in enumerate(selected):
        current_raw = row["actual_spend"].strip()
        if not current_raw:
            results.append({**row, "previous_actual_spend": "", "formula": "NOT COMPUTED — actual_spend is NULL", "growth": "NULL", "status": f"FLAGGED: {row['notes'].strip() or 'missing actual_spend'}"})
            continue

        current = float(current_raw)
        previous_period = None
        if growth_type == "MoM" and index > 0:
            previous_period = selected[index - 1]
        elif growth_type == "YoY":
            year, month = row["period"].split("-")
            previous_period = by_period.get(f"{int(year) - 1:04d}-{month}")

        if not previous_period or not previous_period["actual_spend"].strip():
            formula = "NOT COMPUTED — previous comparison value is unavailable"
            growth = "NULL"
            status = "FLAGGED: previous value is missing"
            previous_value = ""
        else:
            previous_value = float(previous_period["actual_spend"])
            if previous_value == 0:
                formula = "NOT COMPUTED — previous value is zero"
                growth = "NULL"
                status = "FLAGGED: division by zero"
            else:
                growth_value = ((current - previous_value) / previous_value) * 100
                formula = f"(({current:.1f} - {previous_value:.1f}) / {previous_value:.1f}) × 100"
                growth = f"{growth_value:+.1f}%"
                status = "OK"
        results.append({**row, "previous_actual_spend": f"{previous_value:.1f}" if previous_value != "" else "", "formula": formula, "growth": growth, "status": status})
    return results


def write_output(rows: list[dict], output_path: str) -> None:
    fields = ["period", "ward", "category", "actual_spend", "previous_actual_spend", "formula", "growth", "status", "notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward")
    parser.add_argument("--category", required=True, help="Exactly one category")
    parser.add_argument("--growth-type", required=True, choices=sorted(VALID_GROWTH_TYPES), help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()

    if args.ward.strip().lower() in {"all", "all wards", "all-wards"}:
        parser.error("All-ward aggregation is not permitted.")
    rows, null_rows = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_rows)}.")
    for row in null_rows:
        print(f"FLAGGED: {row['period']} | {row['ward']} | {row['category']} | {row['notes'].strip() or 'No reason supplied'}")
    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(result, args.output)
    print(f"Done. {len(result)} rows written to {args.output}")


if __name__ == "__main__":
    main()

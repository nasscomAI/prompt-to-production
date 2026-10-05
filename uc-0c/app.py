"""
UC-0C app.py — Budget growth calculator CLI.
Reads a budget CSV, filters to one ward/category, computes MoM or YoY growth,
and writes a row-wise analysis CSV.
"""
import argparse
import csv
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_rows(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError("Input CSV is empty")

    missing = [col for col in REQUIRED_COLUMNS if col not in rows[0]]
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {', '.join(missing)}")

    normalized_rows: list[dict[str, Any]] = []
    for row in rows:
        normalized_row = {
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "budgeted_amount": float(row["budgeted_amount"]),
            "actual_spend": None if row.get("actual_spend", "").strip() == "" else float(row["actual_spend"]),
            "notes": row.get("notes", "").strip(),
        }
        normalized_rows.append(normalized_row)

    return normalized_rows


def filter_rows(rows: list[dict[str, Any]], ward: str, category: str) -> list[dict[str, Any]]:
    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'")
    return filtered


def compute_growth(rows: list[dict[str, Any]], growth_type: str) -> list[dict[str, Any]]:
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth_type must be either 'MoM' or 'YoY'")

    sorted_rows = sorted(rows, key=lambda row: row["period"])
    period_lookup = {(row["period"], row["ward"], row["category"]): row for row in sorted_rows}
    results: list[dict[str, Any]] = []
    previous_row: dict[str, Any] | None = None

    for row in sorted_rows:
        current_value = row["actual_spend"]
        if current_value is None:
            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "growth_type": growth_type,
                    "actual_spend": "",
                    "previous_value": "",
                    "growth_percent": "",
                    "formula": "n/a",
                    "status": "flagged_null",
                    "reason": row["notes"] or "No reason provided",
                }
            )
            previous_row = row
            continue

        previous_value: float | None = None
        if growth_type == "MoM":
            if previous_row is None or previous_row["actual_spend"] is None:
                growth_value = ""
                formula = "n/a"
                status = "not_computable"
                reason = "No prior period value available"
            else:
                previous_value = previous_row["actual_spend"]
                growth_value = ((current_value - previous_value) / previous_value) * 100 if previous_value else None
                formula = f"(({current_value:.2f} - {previous_value:.2f}) / {previous_value:.2f}) * 100"
                status = "computed"
                reason = ""
        else:
            year_str, month_str = row["period"].split("-", 1)
            prior_period = f"{int(year_str) - 1}-{month_str}"
            prior_row = period_lookup.get((prior_period, row["ward"], row["category"]))
            if prior_row is None or prior_row["actual_spend"] is None:
                growth_value = ""
                formula = "n/a"
                status = "not_computable"
                reason = "No prior-year data available in dataset"
            else:
                previous_value = prior_row["actual_spend"]
                growth_value = ((current_value - previous_value) / previous_value) * 100 if previous_value else None
                formula = f"(({current_value:.2f} - {previous_value:.2f}) / {previous_value:.2f}) * 100"
                status = "computed"
                reason = ""

        results.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "growth_type": growth_type,
                "actual_spend": f"{current_value:.2f}" if current_value is not None else "",
                "previous_value": f"{previous_value:.2f}" if previous_value is not None else "",
                "growth_percent": "" if growth_value in {None, ""} else f"{growth_value:+.1f}%",
                "formula": formula,
                "status": status,
                "reason": reason,
            }
        )
        previous_row = row

    return results


def write_output(output_path: Path, results: list[dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "period",
                "ward",
                "category",
                "growth_type",
                "actual_spend",
                "previous_value",
                "growth_percent",
                "formula",
                "status",
                "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute budget growth for one ward/category")
    parser.add_argument("--input", required=True, help="Path to the budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward to analyze")
    parser.add_argument("--category", required=True, help="Category to analyze")
    parser.add_argument("--growth-type", default=None, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write the CSV output")
    args = parser.parse_args()

    if not args.growth_type:
        raise ValueError("Growth type is required; specify 'MoM' or 'YoY'")

    csv_path = Path(args.input)
    output_path = Path(args.output)

    rows = load_rows(csv_path)
    filtered = filter_rows(rows, args.ward, args.category)
    results = compute_growth(filtered, args.growth_type)
    write_output(output_path, results)

    print(f"Wrote growth analysis to {output_path}")


if __name__ == "__main__":
    main()

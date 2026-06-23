"""
UC-0C - Ward budget growth calculator.

Computes growth only for an explicit ward/category scope and explicit formula.
Null actual_spend rows are reported before calculation and flagged in output.
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

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "growth_type",
    "previous_period",
    "previous_actual_spend",
    "formula",
    "growth_percent",
    "flag",
    "null_reason",
]

SUPPORTED_GROWTH_TYPES = {"MoM"}
AGGREGATE_TOKENS = {"", "all", "any", "*", "all wards", "all categories"}


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Read the CSV, validate required columns, and report null actual_spend rows.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS.difference(columns)
        if missing:
            missing_list = ", ".join(sorted(missing))
            raise ValueError(f"Input CSV is missing required columns: {missing_list}")

        rows = list(reader)

    null_rows = [row for row in rows if not (row.get("actual_spend") or "").strip()]
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_rows)}")
    for row in null_rows:
        print(
            "NULL actual_spend: "
            f"{row['period']} | {row['ward']} | {row['category']} | "
            f"reason: {row.get('notes', '').strip() or 'No reason provided'}"
        )

    return rows, null_rows


def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict]:
    """
    Return a period table for one ward/category with the formula shown per row.
    """
    _validate_scope(ward, category, growth_type)

    scoped_rows = [
        row
        for row in rows
        if row.get("ward") == ward and row.get("category") == category
    ]
    if not scoped_rows:
        raise ValueError(f"No rows found for ward={ward!r}, category={category!r}")

    scoped_rows.sort(key=lambda row: row["period"])
    output_rows = []
    previous = None

    for row in scoped_rows:
        actual_text = (row.get("actual_spend") or "").strip()
        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": actual_text,
            "growth_type": growth_type,
            "previous_period": previous["period"] if previous else "",
            "previous_actual_spend": (previous.get("actual_spend") or "").strip() if previous else "",
            "formula": "",
            "growth_percent": "",
            "flag": "",
            "null_reason": "",
        }

        if not actual_text:
            result["flag"] = "NEEDS_REVIEW"
            result["null_reason"] = (row.get("notes") or "").strip() or "actual_spend is blank"
            result["formula"] = "Not computed because current actual_spend is NULL."
        elif previous is None:
            result["flag"] = "BASE_PERIOD"
            result["formula"] = "Not computed because there is no previous period."
        else:
            previous_actual_text = (previous.get("actual_spend") or "").strip()
            if not previous_actual_text:
                result["flag"] = "NEEDS_REVIEW"
                result["null_reason"] = (
                    (previous.get("notes") or "").strip()
                    or "previous actual_spend is blank"
                )
                result["formula"] = "Not computed because previous actual_spend is NULL."
            else:
                actual = float(actual_text)
                previous_actual = float(previous_actual_text)
                if previous_actual == 0:
                    result["flag"] = "NEEDS_REVIEW"
                    result["null_reason"] = "previous actual_spend is zero"
                    result["formula"] = "Not computed because previous actual_spend is zero."
                else:
                    growth = ((actual - previous_actual) / previous_actual) * 100
                    result["formula"] = (
                        f"(({actual:.1f} - {previous_actual:.1f}) / "
                        f"{previous_actual:.1f}) * 100"
                    )
                    result["growth_percent"] = f"{growth:+.1f}%"

        output_rows.append(result)
        previous = row

    return output_rows


def _validate_scope(ward: str, category: str, growth_type: str):
    if _is_aggregate_token(ward):
        raise ValueError("Refusing all-ward aggregation: provide one explicit --ward.")
    if _is_aggregate_token(category):
        raise ValueError("Refusing all-category aggregation: provide one explicit --category.")
    if not growth_type:
        raise ValueError("Refusing to guess formula: provide --growth-type, for example MoM.")
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        supported = ", ".join(sorted(SUPPORTED_GROWTH_TYPES))
        raise ValueError(f"Unsupported --growth-type {growth_type!r}. Supported: {supported}.")


def _is_aggregate_token(value: str) -> bool:
    return (value or "").strip().lower() in AGGREGATE_TOKENS


def write_output(rows: list[dict], output_path: str):
    output = Path(output_path)
    if output.parent and str(output.parent) != ".":
        output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name; all-ward aggregation is refused")
    parser.add_argument("--category", help="Exact category name; all-category aggregation is refused")
    parser.add_argument("--growth-type", help="Growth formula to use; currently supports MoM")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    try:
        rows, _null_rows = load_dataset(args.input)
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(output_rows, args.output)
    except ValueError as exc:
        raise SystemExit(f"REFUSED: {exc}") from exc

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
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
FORMULA = "MoM = ((current_actual - previous_actual) / previous_actual) * 100"


def normalize_lookup(value: str) -> str:
    return " ".join(value.replace("—", "-").replace("–", "-").strip().casefold().split())


def load_dataset(input_path: str) -> list[dict]:
    with Path(input_path).open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing a header row.")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(sorted(missing))}")
        return list(reader)


def resolve_filter(label: str, value: str | None, available: set[str]) -> str | None:
    if value is None:
        return None
    normalized = normalize_lookup(value)
    if normalized in {"all", "all wards", "all categories", "*"}:
        raise ValueError("Refusing all-ward or all-category aggregation. Use explicit ward/category values or omit both to write the full per-ward per-category table.")
    for candidate in sorted(available):
        if normalize_lookup(candidate) == normalized:
            return candidate
    raise ValueError(f"Unknown {label}: {value}")


def compute_growth(rows: list[dict], growth_type: str | None, ward: str | None = None, category: str | None = None) -> list[dict]:
    if not growth_type:
        raise ValueError("Refusing to guess a growth type. Supply --growth-type MoM.")
    if growth_type.strip().casefold() != "mom":
        raise ValueError("Unsupported growth type. This implementation supports MoM only.")
    if bool(ward) != bool(category):
        raise ValueError("Provide both --ward and --category together, or omit both to write the full table.")

    wards = {row["ward"] for row in rows}
    categories = {row["category"] for row in rows}
    selected_ward = resolve_filter("ward", ward, wards)
    selected_category = resolve_filter("category", category, categories)

    filtered = rows
    if selected_ward and selected_category:
        filtered = [
            row for row in rows
            if row["ward"] == selected_ward and row["category"] == selected_category
        ]

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in filtered:
        grouped[(row["ward"], row["category"])].append(row)

    output_rows: list[dict] = []
    for ward_name, category_name in sorted(grouped):
        series = sorted(grouped[(ward_name, category_name)], key=lambda item: item["period"])
        for index, row in enumerate(series):
            previous_row = series[index - 1] if index > 0 else None
            actual = float(row["actual_spend"]) if row["actual_spend"] else None
            previous_actual = None
            if previous_row and previous_row["actual_spend"]:
                previous_actual = float(previous_row["actual_spend"])

            result = {
                "period": row["period"],
                "ward": ward_name,
                "category": category_name,
                "growth_type": "MoM",
                "actual_spend": f"{actual:.1f}" if actual is not None else "",
                "previous_period": previous_row["period"] if previous_row else "",
                "previous_actual_spend": f"{previous_actual:.1f}" if previous_actual is not None else "",
                "growth_percent": "",
                "formula": FORMULA,
                "status": "",
                "null_reason": row["notes"],
                "notes": row["notes"],
            }

            if actual is None:
                result["status"] = "NULL_ACTUAL"
            elif previous_row is None:
                result["status"] = "NO_PRIOR_PERIOD"
            elif previous_actual is None:
                result["status"] = "PREVIOUS_NULL"
                result["null_reason"] = f"{previous_row['period']} actual_spend is null: {previous_row['notes']}"
            elif previous_actual == 0:
                result["status"] = "PREVIOUS_ZERO"
                result["null_reason"] = f"{previous_row['period']} actual_spend is zero"
            else:
                growth = ((actual - previous_actual) / previous_actual) * 100
                result["growth_percent"] = f"{growth:+.1f}%"
                result["status"] = "OK"

            output_rows.append(result)

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C per-ward budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Specific ward to filter")
    parser.add_argument("--category", help="Specific category to filter")
    parser.add_argument("--growth-type", help="Growth type to calculate. Use MoM.")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.growth_type, args.ward, args.category)

    fieldnames = [
        "period",
        "ward",
        "category",
        "growth_type",
        "actual_spend",
        "previous_period",
        "previous_actual_spend",
        "growth_percent",
        "formula",
        "status",
        "null_reason",
        "notes",
    ]
    with Path(args.output).open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} rows to {args.output}")

if __name__ == "__main__":
    main()

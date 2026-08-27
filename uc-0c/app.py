"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def parse_float(value: str):
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid numeric value: {value}")


def load_dataset(file_path: str) -> list[dict]:
    rows = []
    with open(file_path, encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")

        for col in REQUIRED_COLUMNS:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")

        for line_number, raw_row in enumerate(reader, start=2):
            period = raw_row["period"].strip()
            try:
                datetime.strptime(period, "%Y-%m")
            except ValueError:
                raise ValueError(f"Invalid period format on line {line_number}: {period}")

            actual_spend = parse_float(raw_row["actual_spend"])
            budgeted_amount = parse_float(raw_row["budgeted_amount"])
            if budgeted_amount is None:
                raise ValueError(f"Missing budgeted_amount on line {line_number}")

            rows.append({
                "period": period,
                "ward": raw_row["ward"].strip(),
                "category": raw_row["category"].strip(),
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": raw_row["notes"].strip(),
                "line_number": line_number,
            })

    null_rows = [r for r in rows if r["actual_spend"] is None]
    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend rows before computing growth:")
        for row in null_rows:
            print(f"  {row['period']} · {row['ward']} · {row['category']} · note: {row['notes']}")
    return rows


def normalize_text(value: str) -> str:
    return value.replace(" - ", " – ").strip()


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if not growth_type:
        raise ValueError("--growth-type is required. Please specify MoM or YoY.")

    growth_type = growth_type.strip()
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError(f"Unsupported growth type: {growth_type}. Supported values: MoM, YoY.")

    ward = normalize_text(ward)
    category = category.strip()
    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    sorted_rows = sorted(filtered, key=lambda r: r["period"])

    output = []
    for idx, row in enumerate(sorted_rows):
        formula = ""
        growth = ""
        flag = ""
        notes = row["notes"] or ""
        if row["actual_spend"] is None:
            flag = "NULL"
            growth = "NOT COMPUTED"
            formula = "actual_spend is null"
            if not notes:
                notes = "No note provided"
        else:
            if growth_type == "MoM":
                if idx == 0:
                    growth = "N/A"
                    formula = "No prior month to compare"
                else:
                    previous = sorted_rows[idx - 1]
                    if previous["actual_spend"] is None:
                        flag = "NULL PRIOR MONTH"
                        growth = "NOT COMPUTED"
                        formula = "Previous month's actual_spend is null"
                    else:
                        growth_value = ((row["actual_spend"] - previous["actual_spend"]) / previous["actual_spend"]) * 100
                        growth = f"{growth_value:+.1f}%"
                        formula = f"({row['actual_spend']} - {previous['actual_spend']}) / {previous['actual_spend']} * 100"
            else:
                if idx < 12:
                    growth = "N/A"
                    formula = "Need 12 months of prior data for YoY"
                else:
                    prior_year = sorted_rows[idx - 12]
                    if prior_year["actual_spend"] is None:
                        flag = "NULL PRIOR YEAR"
                        growth = "NOT COMPUTED"
                        formula = "Prior year's actual_spend is null"
                    else:
                        growth_value = ((row["actual_spend"] - prior_year["actual_spend"]) / prior_year["actual_spend"]) * 100
                        growth = f"{growth_value:+.1f}%"
                        formula = f"({row['actual_spend']} - {prior_year['actual_spend']}) / {prior_year['actual_spend']} * 100"

        if not notes:
            if growth == "NOT COMPUTED":
                notes = "Not computed"
            else:
                notes = "Computed"

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "NULL" if row["actual_spend"] is None else f"{row['actual_spend']:.1f}",
            "growth": growth,
            "formula": formula,
            "flag": flag,
            "notes": notes,
        })

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to compute growth for")
    parser.add_argument("--category", required=True, help="Category name to compute growth for")
    parser.add_argument("--growth-type", required=True, help="Growth type to calculate (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula", "flag", "notes"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

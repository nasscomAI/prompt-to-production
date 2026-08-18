"""
UC-0C app.py — Number That Looks Right
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


def parse_float(value):
    value = value.strip()
    return None if value == "" else float(value)


def load_dataset(path):
    records = []
    with open(path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            records.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"].strip()),
                "actual_spend": parse_float(row.get("actual_spend", "")),
                "notes": (row.get("notes") or "").strip(),
            })

    return records


def _parse_period(period):
    return datetime.strptime(period, "%Y-%m")


def _format_pct(value):
    return f"{value:+.1f}%"


def compute_growth(records, ward, category, growth_type):
    filtered = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    filtered.sort(key=lambda row: _parse_period(row["period"]))
    period_index = {row["period"]: row for row in filtered}

    output_rows = []
    for idx, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        notes = row["notes"]
        previous_period = ""
        previous_actual = None
        growth_pct = ""
        formula = ""
        status = ""

        if actual is None:
            status = "NULL actual_spend; not computed"
            formula = "n/a"
        else:
            if growth_type == "MoM":
                if idx == 0:
                    status = "No prior month to compute MoM"
                    formula = "n/a"
                else:
                    previous = filtered[idx - 1]
                    previous_period = previous["period"]
                    previous_actual = previous["actual_spend"]
                    if previous_actual is None:
                        status = "Previous actual_spend is NULL; not computed"
                        formula = "n/a"
                    elif previous_actual == 0:
                        status = "Previous actual_spend is zero; not computed"
                        formula = "n/a"
                    else:
                        change = actual - previous_actual
                        pct = (change / previous_actual) * 100
                        growth_pct = _format_pct(pct)
                        formula = f"({actual} - {previous_actual}) / {previous_actual} * 100"
                        status = "Computed"
            elif growth_type == "YoY":
                year, month = map(int, period.split("-"))
                target = f"{year - 1:04d}-{month:02d}"
                previous = period_index.get(target)
                if previous is None:
                    status = "No prior year period to compute YoY"
                    formula = "n/a"
                else:
                    previous_actual = previous["actual_spend"]
                    previous_period = target
                    if previous_actual is None:
                        status = "Prior year actual_spend is NULL; not computed"
                        formula = "n/a"
                    elif previous_actual == 0:
                        status = "Prior year actual_spend is zero; not computed"
                        formula = "n/a"
                    else:
                        change = actual - previous_actual
                        pct = (change / previous_actual) * 100
                        growth_pct = _format_pct(pct)
                        formula = f"({actual} - {previous_actual}) / {previous_actual} * 100"
                        status = "Computed"
            else:
                raise ValueError(f"Unsupported growth type: {growth_type}")

        output_rows.append({
            "period": period,
            "actual_spend": "NULL" if actual is None else f"{actual:.1f}",
            "previous_period": previous_period,
            "previous_actual_spend": "NULL" if previous_actual is None else ("" if previous_period == "" else f"{previous_actual:.1f}"),
            "growth_pct": growth_pct,
            "formula": formula,
            "status": status,
            "notes": notes,
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category name to filter")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type to compute")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    records = load_dataset(args.input)
    result_rows = compute_growth(records, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period",
        "actual_spend",
        "previous_period",
        "previous_actual_spend",
        "growth_pct",
        "formula",
        "status",
        "notes",
    ]
    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

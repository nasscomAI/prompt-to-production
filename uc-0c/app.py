"""
UC-0C app.py – Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import csv
from collections import defaultdict


def load_dataset(input_path: str):
    """
    Read the ward budget CSV, validate columns, report null count and rows.
    Returns: list of row dicts.
    """
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not all(col in reader.fieldnames for col in required_cols):
            raise ValueError(f"Missing required columns. Expected: {required_cols}, got: {reader.fieldnames}")
        rows = list(reader)

    null_rows = [r for r in rows if r["actual_spend"] in ("", None)]
    if null_rows:
        print(f"NOTE: {len(null_rows)} row(s) have null actual_spend:")
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r.get('notes', '')}")

    return rows

def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for a specific ward+category only.
    growth_type must be 'MoM' or 'YoY' — never guessed.
    Returns: list of dicts with period, actual_spend, growth_value, formula_used, flag.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("growth_type must be 'MoM' or 'YoY' — must be explicitly specified, not guessed.")

    def normalize(s):
        return s.replace(chr(0x2013), "-").replace(chr(0x2014), "-").replace(chr(0x2011), "-").strip()

    filtered = [r for r in rows if normalize(r["ward"]) == normalize(ward) and normalize(r["category"]) == normalize(category)]
    if not filtered:
        raise ValueError(f"No rows found for ward='{ward}' category='{category}'. Refusing to guess or substitute.")

    filtered.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in filtered}

    def prev_period(period: str) -> str:
        year, month = map(int, period.split("-"))
        if growth_type == "MoM":
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        else:
            year -= 1
        return f"{year:04d}-{month:02d}"

    results = []
    for r in filtered:
        period = r["period"]
        actual_raw = r["actual_spend"]
        prev_p = prev_period(period)
        prev_row = by_period.get(prev_p)

        formula = f"({growth_type}) (current - previous) / previous * 100, comparing {period} to {prev_p}"

        if actual_raw in ("", None):
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": "NULL", "growth_value": "NULL",
                "formula_used": formula,
                "flag": f"NULL — actual_spend missing. Reason: {r.get('notes', 'not specified')}",
            })
            continue

        if prev_row is None or prev_row["actual_spend"] in ("", None):
            reason = "no prior period in dataset" if prev_row is None else f"prior period actual_spend is null (reason: {prev_row.get('notes', 'not specified')})"
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": actual_raw, "growth_value": "NULL",
                "formula_used": formula,
                "flag": f"NULL — cannot compute, {reason}",
            })
            continue

        current = float(actual_raw)
        previous = float(prev_row["actual_spend"])
        if previous == 0:
            growth = "NULL"
            flag = "NULL — previous period value is 0, division undefined"
        else:
            growth = round((current - previous) / previous * 100, 1)
            flag = ""

        results.append({
            "period": period, "ward": ward, "category": category,
            "actual_spend": actual_raw, "growth_value": growth,
            "formula_used": formula, "flag": flag,
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=False, choices=["MoM", "YoY"],
                         help="MoM or YoY — required, will refuse if omitted")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit("ERROR: --growth-type is required (MoM or YoY). Refusing to guess.")

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_value", "formula_used", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
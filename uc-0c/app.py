"""
UC-0C - Number That Looks Right
Computes per-ward per-category growth (MoM or YoY) from the ward budget
dataset. Never aggregates across wards/categories, never silently skips
nulls, and never guesses a growth type.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            sys.exit(f"ERROR: input file is missing required columns: {missing_cols}")
        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    print(f"[load_dataset] {len(rows)} rows loaded. {len(null_rows)} rows have null actual_spend:",
          file=sys.stderr)
    for r in null_rows:
        reason = r["notes"].strip() or "no reason given"
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {reason}",
              file=sys.stderr)

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        sys.exit(f"ERROR: no rows found for ward='{ward}' category='{category}'. "
                  f"Check exact spelling (e.g. en-dash in ward names).")

    output = []

    if growth_type == "YoY":
        for r in filtered:
            output.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": r["actual_spend"] or "NULL",
                "growth_pct": "N/A",
                "formula": "YoY not computable - dataset contains only one year (2024)",
            })
        return output

    prev_row = None
    for r in filtered:
        curr_val = r["actual_spend"].strip()
        entry = {"period": r["period"], "ward": ward, "category": category}

        if not curr_val:
            reason = r["notes"].strip() or "no reason given"
            entry["actual_spend"] = "NULL"
            entry["growth_pct"] = "NULL"
            entry["formula"] = f"N/A - actual_spend missing ({reason})"
        elif prev_row is None:
            entry["actual_spend"] = curr_val
            entry["growth_pct"] = "N/A"
            entry["formula"] = "N/A - no prior period available for MoM"
        elif not prev_row["actual_spend"].strip():
            entry["actual_spend"] = curr_val
            entry["growth_pct"] = "NULL"
            entry["formula"] = f"N/A - previous period ({prev_row['period']}) actual_spend is null"
        else:
            curr = float(curr_val)
            prev = float(prev_row["actual_spend"])
            growth = ((curr - prev) / prev) * 100
            entry["actual_spend"] = curr_val
            entry["growth_pct"] = f"{growth:.1f}%"
            entry["formula"] = f"(({curr}-{prev})/{prev})*100 = {growth:.1f}%"

        output.append(entry)
        prev_row = r

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                         help="Exact ward name, e.g. 'Ward 1 - Kasba'. Required - no cross-ward aggregation.")
    parser.add_argument("--category", required=True,
                         help="Exact category name. Required - no cross-category aggregation.")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                         help="Must be explicitly specified. Never guessed.")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"[compute_growth] Wrote {len(result)} rows to {args.output}")

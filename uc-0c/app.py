"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Enforces single-ward single-category calculation, refuses cross-ward aggregation, flags deliberate nulls, and outputs explicit formulas.
"""
import argparse
import csv
import os
import sys


def load_dataset(file_path: str):
    """
    Reads the CSV, validates columns, and reports deliberate nulls.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    records = []
    null_rows = []
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns. Expected {required_cols}, got {reader.fieldnames}")

        for idx, row in enumerate(reader, start=2):
            val_str = (row.get("actual_spend") or "").strip()
            if val_str == "" or val_str.lower() == "null":
                null_rows.append((idx, row["period"], row["ward"], row["category"], row.get("notes", "")))
            records.append(row)

    print(f"Loaded {len(records)} records. Identified {len(null_rows)} deliberate null actual_spend row(s):")
    for r in null_rows:
        print(f"  • Line {r[0]} | Period: {r[1]} | Ward: {r[2]} | Category: {r[3]} | Reason: {r[4]}")

    return records


def compute_growth(records: list, ward: str, category: str, growth_type: str, output_path: str):
    """
    Computes per-period growth rate for specified ward and category.
    """
    if not ward or ward.lower() in ["all", "any", "none", "*"]:
        raise ValueError("REFUSAL: All-ward aggregation is strictly prohibited. You must specify a single ward.")
    if not category or category.lower() in ["all", "any", "none", "*"]:
        raise ValueError("REFUSAL: All-category aggregation is strictly prohibited. You must specify a single category.")
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError("REFUSAL: Growth type must be explicitly specified as 'MoM' or 'YoY'. Do not guess.")

    # Filter rows matching ward and category
    filtered = [
        r for r in records
        if r["ward"].strip().lower() == ward.strip().lower()
        and r["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    prev_spend = None

    for i, row in enumerate(filtered):
        period = row["period"]
        budgeted = row["budgeted_amount"]
        spend_str = (row.get("actual_spend") or "").strip()
        notes = (row.get("notes") or "").strip()

        if spend_str == "" or spend_str.lower() == "null":
            # Null actual spend row
            out_row = {
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth_type": growth_type.upper(),
                "growth_rate": "NULL",
                "formula": "Not computed (missing actual_spend data)",
                "status_notes": f"FLAGGED_NULL: {notes}" if notes else "FLAGGED_NULL: Missing spend data",
            }
            prev_spend = None
        else:
            actual_val = float(spend_str)
            if i == 0 or prev_spend is None:
                if i == 0:
                    formula_str = "Base period (no prior month available)"
                    growth_rate_str = "N/A"
                    status = "Base period"
                else:
                    formula_str = "Not computed (prior month actual_spend was NULL)"
                    growth_rate_str = "N/A"
                    status = "Prior period was NULL"
            else:
                growth_pct = ((actual_val - prev_spend) / prev_spend) * 100.0
                sign = "+" if growth_pct > 0 else ""
                growth_rate_str = f"{sign}{growth_pct:.1f}%"
                formula_str = f"(({actual_val} - {prev_spend}) / {prev_spend}) * 100"
                status = "OK"

            out_row = {
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": f"{actual_val:.1f}",
                "growth_type": growth_type.upper(),
                "growth_rate": growth_rate_str,
                "formula": formula_str,
                "status_notes": status,
            }
            prev_spend = actual_val

        output_rows.append(out_row)

    # Write output CSV
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula",
        "status_notes",
    ]
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nSuccessfully generated {len(output_rows)} rows to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Target category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", default="MoM", dest="growth_type", help="Growth metric: MoM or YoY")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    records = load_dataset(args.input)
    compute_growth(
        records=records,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()

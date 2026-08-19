"""
UC-0C — Number That Looks Right
Guided by RICE specifications in agents.md and skills.md.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str):
    """
    Skill: load_dataset
    Reads ward_budget.csv, validates columns, and flags null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget CSV file not found: {input_path}")

    rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            actual = row.get("actual_spend", "").strip()
            if actual == "":
                row["actual_spend_clean"] = None
                null_rows.append((idx, row))
            else:
                try:
                    row["actual_spend_clean"] = float(actual)
                except ValueError:
                    row["actual_spend_clean"] = None
                    null_rows.append((idx, row))
            rows.append(row)

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Computes per-period growth for a specific ward & category.
    Refuses multi-ward or multi-category aggregation.
    Explicitly displays formula and flags null rows.
    """
    if not growth_type:
        print("ERROR: Refusal triggered — --growth-type (MoM or YoY) must be specified explicitly.", file=sys.stderr)
        sys.exit(1)

    if growth_type.upper() not in ["MOM", "YOY"]:
        print(f"ERROR: Refusal triggered — Unsupported growth type '{growth_type}'. Must be MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    if not ward or ward.lower() == "all":
        print("ERROR: Refusal triggered — All-ward aggregation is not permitted. Specify an exact ward.", file=sys.stderr)
        sys.exit(1)

    if not category or category.lower() == "all":
        print("ERROR: Refusal triggered — All-category aggregation is not permitted. Specify an exact category.", file=sys.stderr)
        sys.exit(1)

    # Filter rows by ward and category
    filtered = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    if not filtered:
        print(f"ERROR: No matching rows found for ward='{ward}' and category='{category}'.", file=sys.stderr)
        sys.exit(1)

    # Sort filtered rows by period (YYYY-MM)
    filtered.sort(key=lambda r: r.get("period", ""))

    results = []
    for i, row in enumerate(filtered):
        period = row.get("period", "")
        budgeted = row.get("budgeted_amount", "")
        curr_val = row.get("actual_spend_clean")
        notes = row.get("notes", "").strip()

        res_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": row.get("actual_spend", "") if curr_val is not None else "NULL",
            "growth_type": growth_type.upper(),
            "growth_percentage": "",
            "formula": "",
            "notes": notes,
            "flag": ""
        }

        # 1. Handle current row being NULL
        if curr_val is None:
            res_row["growth_percentage"] = "NULL"
            res_row["formula"] = "N/A (Current period actual spend is NULL)"
            res_row["flag"] = "NULL_SPEND_FLAGGED"
            results.append(res_row)
            continue

        # 2. First period in dataset (no prior period)
        if i == 0:
            res_row["growth_percentage"] = "N/A"
            res_row["formula"] = "N/A (First period in dataset)"
            res_row["flag"] = ""
            results.append(res_row)
            continue

        # 3. MoM Calculation
        prev_row = filtered[i - 1]
        prev_val = prev_row.get("actual_spend_clean")
        prev_period = prev_row.get("period", "")

        if prev_val is None:
            res_row["growth_percentage"] = "NULL"
            res_row["formula"] = f"N/A (Previous period {prev_period} spend is NULL)"
            res_row["flag"] = "PREVIOUS_PERIOD_NULL"
        elif prev_val == 0:
            res_row["growth_percentage"] = "N/A"
            res_row["formula"] = f"N/A (Previous period {prev_period} spend is 0)"
            res_row["flag"] = "DIVISION_BY_ZERO"
        else:
            growth_pct = ((curr_val - prev_val) / prev_val) * 100.0
            sign = "+" if growth_pct >= 0 else "−"
            res_row["growth_percentage"] = f"{sign}{abs(growth_pct):.1f}%"
            res_row["formula"] = f"({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f} * 100"
            res_row["flag"] = ""

        results.append(res_row)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = [
        "period", "ward", "category", "budgeted_amount", "actual_spend",
        "growth_type", "growth_percentage", "formula", "notes", "flag"
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Done. Growth output table written to {args.output}")


if __name__ == "__main__":
    main()

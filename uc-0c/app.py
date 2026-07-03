"""
UC-0C app.py — Ward Budget Growth Calculator
Enforces: per-ward per-category only, null flagging, formula display, growth-type refusal.
"""
import argparse
import csv


def load_dataset(file_path: str) -> list:
    """
    Reads the budget CSV file, validates columns, and reports null actual_spend rows.
    Returns: list of row dicts.
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    rows = []
    null_rows = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV is missing required columns. Expected: {required_columns}")
        for row in reader:
            # Normalize null values
            if row["actual_spend"].strip() == "":
                row["actual_spend"] = None
                null_rows.append(row)
            else:
                row["actual_spend"] = float(row["actual_spend"])
            row["budgeted_amount"] = float(row["budgeted_amount"])
            rows.append(row)

    print(f"\n[load_dataset] Loaded {len(rows)} rows from {file_path}")
    print(f"[load_dataset] Found {len(null_rows)} null actual_spend rows:")
    for nr in null_rows:
        reason = nr["notes"].strip() if nr["notes"].strip() else "No reason provided"
        print(f"  → {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {reason}")
    print()

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters rows by ward and category, computes MoM or YoY growth per period.
    Each row in output includes: period, actual_spend, budgeted_amount, growth_pct, formula, notes.
    """
    if not growth_type:
        raise ValueError("--growth-type is required. Please specify 'MoM' or 'YoY'. Cannot guess.")

    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        raise ValueError(f"Invalid growth-type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    # Filter to requested ward and category
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'.")

    # Sort chronologically by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        budgeted = row["budgeted_amount"]
        notes = row["notes"].strip()

        # First period: no previous data to compare
        if i == 0:
            results.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": actual if actual is not None else "NULL",
                "growth_pct": "N/A",
                "formula": "N/A (first period)",
                "notes": notes,
            })
            continue

        # Determine the comparison period (previous or same month last year)
        if growth_type == "MOM":
            compare_row = filtered[i - 1]
        else:  # YoY - look for same month, previous year
            current_year = int(period[:4])
            current_month = period[5:]
            prev_year_period = f"{current_year - 1}-{current_month}"
            compare_rows = [r for r in filtered if r["period"] == prev_year_period]
            compare_row = compare_rows[0] if compare_rows else None

        if compare_row is None:
            results.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": actual if actual is not None else "NULL",
                "growth_pct": "N/A",
                "formula": "N/A (no prior period for comparison)",
                "notes": notes,
            })
            continue

        prev_actual = compare_row["actual_spend"]

        # Handle nulls
        if actual is None:
            reason = notes if notes else "null in source data"
            results.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth_pct": "NULL — NOT COMPUTED",
                "formula": f"NULL — not computed because current period spend is null. Reason: {reason}",
                "notes": notes,
            })
            continue

        if prev_actual is None:
            prev_reason = compare_row["notes"].strip() if compare_row["notes"].strip() else "null in source data"
            results.append({
                "period": period,
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "growth_pct": "NULL — NOT COMPUTED",
                "formula": f"NULL — not computed because prior period ({compare_row['period']}) spend is null. Reason: {prev_reason}",
                "notes": notes,
            })
            continue

        # Calculate growth
        growth = ((actual - prev_actual) / prev_actual) * 100
        sign = "+" if growth >= 0 else ""
        formula_str = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"

        results.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "growth_pct": f"{sign}{growth:.1f}%",
            "formula": formula_str,
            "notes": notes,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input",       required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True, help="Ward name (exact match)")
    parser.add_argument("--category",    required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output",      required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refuse all-ward aggregation
    if args.ward.lower() in ("all", "*", "any"):
        print("ERROR: All-ward aggregation is not permitted. Please specify a single ward name.")
        exit(1)

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)

        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                      "growth_pct", "formula", "notes"]

        with open(args.output, mode="w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Done. Growth output written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

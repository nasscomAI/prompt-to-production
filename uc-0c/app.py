"""
UC-0C: Number That Looks Right
Enforces:
- Never aggregate across wards or categories unless explicitly instructed — refuse if asked.
- Flag every null row before computing — report null reason from the notes column.
- Show formula used in every output row alongside the result.
- If --growth-type not specified — refuse and ask, never guess.
"""
import argparse
import csv
import os
import sys


def load_dataset(csv_path: str):
    """
    Reads CSV, validates required columns, checks for null actual_spend rows,
    and logs every null row before returning parsed dataset.
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Budget dataset not found at: {csv_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    null_rows = []

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing_cols = required_cols - set(reader.fieldnames or [])
        if missing_cols:
            raise ValueError(f"Missing required columns in dataset: {missing_cols}")

        for idx, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            if raw_spend == "" or raw_spend.lower() in ("null", "none", "nan"):
                null_rows.append({
                    "line": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "No reason provided")
                })
            rows.append(row)

    print(f"Dataset loaded: {len(rows)} rows. Detected {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  • {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters rows for specific ward and category, calculates growth per period,
    documents the exact formula used, and flags null records.
    """
    # Enforcement 1: Refusal on cross-ward / all-ward aggregation
    if not ward or ward.strip().lower() in ("all", "any", "aggregated", "total"):
        raise ValueError("REFUSAL: Aggregating across wards is explicitly prohibited. You must specify a single ward.")
    if not category or category.strip().lower() in ("all", "any", "aggregated", "total"):
        raise ValueError("REFUSAL: Aggregating across categories is explicitly prohibited. You must specify a single category.")

    # Filter target records
    matched = [
        r for r in rows
        if r.get("ward", "").strip().lower() == ward.strip().lower()
        and r.get("category", "").strip().lower() == category.strip().lower()
    ]

    if not matched:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort strictly by period
    matched.sort(key=lambda x: x.get("period", ""))

    results = []
    prev_spend = None
    prev_period = None

    for r in matched:
        period = r.get("period")
        b_amt = r.get("budgeted_amount")
        spend_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        is_null = (spend_str == "" or spend_str.lower() in ("null", "none", "nan"))

        if is_null:
            growth_rate = "NULL (Flagged)"
            formula = f"FLAGGED NULL: actual_spend missing. Reason: {notes or 'Unspecified'}"
            current_spend_val = None
        else:
            current_spend_val = float(spend_str)
            if growth_type == "MoM":
                if prev_spend is None:
                    if prev_period is None:
                        growth_rate = "Baseline"
                        formula = "Baseline month (no prior period for MoM calculation)"
                    else:
                        growth_rate = "NULL (Prior period missing)"
                        formula = f"Cannot calculate MoM: prior period ({prev_period}) actual_spend was NULL"
                else:
                    growth_val = ((current_spend_val - prev_spend) / prev_spend) * 100
                    growth_rate = f"{growth_val:+.1f}%"
                    formula = f"(({current_spend_val:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            elif growth_type == "YoY":
                growth_rate = "YoY requires multi-year baseline"
                formula = "YoY comparison requires matching period in prior year"
            else:
                raise ValueError(f"Unknown growth type: {growth_type}")

        results.append({
            "period": period,
            "ward": r.get("ward"),
            "category": r.get("category"),
            "budgeted_amount": b_amt,
            "actual_spend": spend_str if not is_null else "NULL",
            "growth_rate": growth_rate,
            "formula": formula,
            "notes": notes,
        })

        prev_spend = current_spend_val
        prev_period = period

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, default=None,
                        help="Growth calculation type: MoM or YoY (MANDATORY, never guessed)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    # Enforcement 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type or args.growth_type.strip().upper() not in ("MOM", "YOY"):
        print("ERROR / REFUSAL: --growth-type is mandatory and cannot be guessed. Specify either '--growth-type MoM' or '--growth-type YoY'.", file=sys.stderr)
        sys.exit(1)

    growth_type = args.growth_type.strip()

    rows, null_rows = load_dataset(args.input)
    growth_results = compute_growth(rows, args.ward, args.category, growth_type)

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_rate", "formula", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"Success: Growth output written to {args.output}")


if __name__ == "__main__":
    main()

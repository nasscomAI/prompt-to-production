"""
UC-0C app.py — Municipal Budget Growth Auditor
RICE-Enforced Implementation
"""
import argparse
import csv
import sys

FORMULA_MOM_STR = "((actual_spend_current - actual_spend_prev) / actual_spend_prev) * 100"
FORMULA_YOY_STR = "((actual_spend_current - actual_spend_yoy) / actual_spend_yoy) * 100"

def load_dataset(input_path: str):
    """
    Loads CSV dataset, identifies null actual_spend rows, and prints audit report.
    Returns list of parsed row dicts.
    """
    rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Dataset missing required columns. Must contain: {required_cols}")

        for i, row in enumerate(reader, start=2):  # Line number including header
            raw_spend = row["actual_spend"].strip()
            if not raw_spend:
                parsed_spend = None
                null_rows.append({
                    "line": i,
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"]
                })
            else:
                try:
                    parsed_spend = float(raw_spend)
                except ValueError:
                    parsed_spend = None
                    null_rows.append({
                        "line": i,
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": f"Invalid float value: {raw_spend}"
                    })

            rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": float(row["budgeted_amount"]),
                "actual_spend": parsed_spend,
                "notes": row["notes"]
            })

    print(f"Loaded {len(rows)} budget rows from {input_path}.")
    print(f"Audit Flag: Found {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Line {nr['line']} [{nr['period']}] {nr['ward']} | {nr['category']} -> Reason: '{nr['notes']}'")

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period growth for a specific ward and category.
    Refuses cross-ward aggregation or missing growth type.
    """
    # 1. Parameter Enforcement Rules
    if not growth_type:
        raise ValueError("REFUSAL: Growth calculation type (--growth-type) is required. Please specify 'MoM' or 'YoY'.")
    
    gt_upper = growth_type.upper()
    if gt_upper not in ["MOM", "YOY"]:
        raise ValueError(f"REFUSAL: Unsupported growth_type '{growth_type}'. Allowed values: 'MoM', 'YoY'.")

    if not ward or not category or "ALL" in ward.upper() or "ALL" in category.upper():
        raise ValueError("REFUSAL: All-ward or cross-category aggregation is strictly prohibited. You must specify a single ward and single category.")

    # 2. Filter dataset for target ward and category, ordered by period
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    if not filtered:
        raise ValueError(f"No records found for Ward '{ward}' and Category '{category}'.")

    # Map period -> row for fast YoY lookup
    period_map = {r["period"]: r for r in filtered}

    results = []
    
    for i, curr in enumerate(filtered):
        curr_spend = curr["actual_spend"]
        curr_period = curr["period"]

        if curr_spend is None:
            growth_str = f"N/A (Null Value Flagged: {curr['notes']})"
            formula_used = "N/A (Null Spend)"
            display_spend = f"NULL (Flagged: {curr['notes']})"
        else:
            display_spend = f"{curr_spend:.1f}"

            if gt_upper == "MOM":
                if i == 0:
                    growth_str = "N/A"
                    formula_used = "N/A (Initial Period)"
                else:
                    prev_spend = filtered[i-1]["actual_spend"]
                    if prev_spend is None:
                        growth_str = f"N/A (Previous Period Null)"
                        formula_used = "N/A (Previous Period Null)"
                    elif prev_spend == 0:
                        growth_str = "N/A (Division by Zero)"
                        formula_used = "N/A (Zero Previous Spend)"
                    else:
                        pct = ((curr_spend - prev_spend) / prev_spend) * 100
                        growth_str = f"{pct:+.1f}%"
                        formula_used = FORMULA_MOM_STR

            elif gt_upper == "YOY":
                # Find prior year period (YYYY-MM -> (YYYY-1)-MM)
                try:
                    year, month = curr_period.split("-")
                    prior_period = f"{int(year)-1:04d}-{month}"
                except Exception:
                    prior_period = None

                prior_row = period_map.get(prior_period) if prior_period else None

                if not prior_row:
                    growth_str = "N/A"
                    formula_used = "N/A (No Prior Year Data)"
                else:
                    prior_spend = prior_row["actual_spend"]
                    if prior_spend is None:
                        growth_str = "N/A (Previous Period Null)"
                        formula_used = "N/A (Previous Period Null)"
                    elif prior_spend == 0:
                        growth_str = "N/A (Division by Zero)"
                        formula_used = "N/A (Zero Prior Year Spend)"
                    else:
                        pct = ((curr_spend - prior_spend) / prior_spend) * 100
                        growth_str = f"{pct:+.1f}%"
                        formula_used = FORMULA_YOY_STR

        results.append({
            "period": curr["period"],
            "ward": curr["ward"],
            "category": curr["category"],
            "budgeted_amount": f"{curr['budgeted_amount']:.1f}",
            "actual_spend": display_spend,
            "growth_pct": growth_str,
            "formula": formula_used,
            "notes": curr["notes"]
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Auditor")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=False, help="Output CSV path")
    args = parser.parse_args()

    # Load dataset & run null audit
    dataset, null_rows = load_dataset(args.input)

    # Compute growth with strict RICE checks
    try:
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"\n[ERROR/REFUSAL] {e}", file=sys.stderr)
        sys.exit(1)

    # Write output CSV if requested
    output_file = args.output or "growth_output.csv"
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes"]
    
    with open(output_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSuccessfully generated {output_file} with {len(results)} rows.")


if __name__ == "__main__":
    main()



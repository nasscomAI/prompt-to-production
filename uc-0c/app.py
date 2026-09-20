"""
UC-0C app.py — Infrastructure Spend Growth Calculator
Follows enforcement rules from agents.md and skills defined in skills.md.
"""
import argparse
import csv
import sys
import os

def load_dataset(input_path: str):
    """
    Reads CSV, validates required columns, and flags null actual_spend rows.
    Returns: (all_rows, null_rows)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    all_rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            raise ValueError(f"CSV missing required columns: {missing}")

        for idx, row in enumerate(reader, start=1):
            spend_raw = row.get("actual_spend", "").strip()
            row_copy = dict(row)
            if spend_raw == "" or spend_raw.lower() == "null":
                row_copy["actual_spend_float"] = None
                null_rows.append(row_copy)
            else:
                try:
                    row_copy["actual_spend_float"] = float(spend_raw)
                except ValueError:
                    row_copy["actual_spend_float"] = None
                    null_rows.append(row_copy)
            
            try:
                row_copy["budgeted_amount_float"] = float(row.get("budgeted_amount", 0))
            except ValueError:
                row_copy["budgeted_amount_float"] = 0.0

            all_rows.append(row_copy)

    print(f"Loaded {len(all_rows)} rows. Flagged {len(null_rows)} null actual_spend rows.")
    for nr in null_rows:
        print(f"  [NULL FLAGGED] Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {nr['notes']}")

    return all_rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates per-period growth for a specific ward and category.
    Refuses all-ward aggregation or unspecified growth-type.
    """
    # Enforcement 1 & Refusal Condition: Refuse all-ward or all-category aggregation
    if ward.strip().upper() in ["ALL", "TOTAL", "AGGREGATE"] or category.strip().upper() in ["ALL", "TOTAL", "AGGREGATE"]:
        print("REFUSAL: Aggregating across all wards or categories is prohibited by enforcement rules.", file=sys.stderr)
        sys.exit(1)

    # Enforcement 4: If growth_type not specified or invalid, refuse
    if not growth_type or growth_type.strip().upper() not in ["MOM", "YOY"]:
        print("REFUSAL: Growth type must be specified explicitly (e.g. MoM or YoY). Never guessing.", file=sys.stderr)
        sys.exit(1)

    growth_type = growth_type.strip().upper()

    # Filter rows for target ward and category
    filtered = [r for r in rows if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]
    if not filtered:
        print(f"Warning: No rows found matching Ward '{ward}' and Category '{category}'")
        return []

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    for i, curr in enumerate(filtered):
        period = curr["period"]
        b_amt = curr["budgeted_amount"]
        act_spend = curr["actual_spend"]
        notes = curr["notes"]
        act_float = curr["actual_spend_float"]

        if growth_type == "MOM":
            formula_str = "MoM % = (Spend[t] - Spend[t-1]) / Spend[t-1] * 100"
            if act_float is None:
                growth_val = "NULL"
                note_out = f"FLAGGED NULL: {notes}" if notes else "FLAGGED NULL: Missing spend data"
            elif i == 0:
                growth_val = "N/A"
                note_out = notes if notes else "Baseline period (no prior month)"
            else:
                prev = filtered[i - 1]
                prev_float = prev["actual_spend_float"]
                if prev_float is None:
                    growth_val = "NULL"
                    note_out = f"Cannot compute: Prior period ({prev['period']}) spend is NULL"
                elif prev_float == 0:
                    growth_val = "N/A"
                    note_out = "Prior period spend is zero"
                else:
                    diff = act_float - prev_float
                    pct = (diff / prev_float) * 100.0
                    sign = "+" if pct > 0 else ""
                    growth_val = f"{sign}{pct:.1f}%"
                    note_out = notes

        elif growth_type == "YOY":
            formula_str = "YoY % = (Spend[t] - Spend[t-12]) / Spend[t-12] * 100"
            if act_float is None:
                growth_val = "NULL"
                note_out = f"FLAGGED NULL: {notes}" if notes else "FLAGGED NULL: Missing spend data"
            elif i < 12:
                growth_val = "N/A"
                note_out = "Baseline period (no prior year data)"
            else:
                prev = filtered[i - 12]
                prev_float = prev["actual_spend_float"]
                if prev_float is None:
                    growth_val = "NULL"
                    note_out = f"Cannot compute: Prior year period ({prev['period']}) spend is NULL"
                elif prev_float == 0:
                    growth_val = "N/A"
                    note_out = "Prior year spend is zero"
                else:
                    diff = act_float - prev_float
                    pct = (diff / prev_float) * 100.0
                    sign = "+" if pct > 0 else ""
                    growth_val = f"{sign}{pct:.1f}%"
                    note_out = notes

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": b_amt,
            "actual_spend": act_spend if act_spend else "NULL",
            "growth_pct": growth_val,
            "formula_used": formula_str,
            "notes": note_out
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Infrastructure Spend Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, dest="growth_type", help="Growth metric formula (e.g. 'MoM' or 'YoY')")
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    all_rows, _ = load_dataset(args.input)
    growth_results = compute_growth(all_rows, args.ward, args.category, args.growth_type)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula_used", "notes"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"Done. Growth results written to {args.output}")

if __name__ == "__main__":
    main()

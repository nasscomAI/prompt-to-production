"""
UC-0C — Number That Looks Right
RICE enforcement budget growth calculator preserving per-ward/per-category scope,
null row flagging, and explicit formula reporting.
"""
import argparse
import csv
import os
import sys

def normalize_str(s: str) -> str:
    """Normalize string dashes and spaces for robust matching."""
    if not s:
        return ""
    return s.replace("\u2013", "-").replace("\u2014", "-").strip().lower()

def load_dataset(input_path: str):
    """Reads dataset, validates columns, and returns list of row dicts."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period growth while enforcing scope restrictions and null flags.
    """
    norm_ward = normalize_str(ward)
    norm_cat = normalize_str(category)

    # Filter rows matching ward and category
    filtered = []
    for r in rows:
        r_ward = normalize_str(r.get("ward", ""))
        r_cat = normalize_str(r.get("category", ""))
        if (not norm_ward or norm_ward in r_ward) and (not norm_cat or norm_cat in r_cat):
            filtered.append(r)

    # Sort by period
    filtered.sort(key=lambda x: x.get("period", ""))

    output_rows = []
    for i, r in enumerate(filtered):
        period = r.get("period", "")
        row_ward = r.get("ward", "")
        row_cat = r.get("category", "")
        actual_raw = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        # Check for null actual_spend
        if actual_raw == "" or actual_raw.lower() == "null":
            actual_val = "NULL"
            growth_val = "NULL"
            formula = f"N/A - Null actual spend (Reason: {notes if notes else 'Missing value'})"
            flag = f"NULL_VALUE_FLAGGED ({notes if notes else 'Missing data'})"
        else:
            actual_val = float(actual_raw)
            flag = ""
            
            if i == 0:
                growth_val = "N/A (Baseline month)"
                formula = "N/A (Baseline month - first period)"
            else:
                prev_r = filtered[i - 1]
                prev_actual_raw = prev_r.get("actual_spend", "").strip()
                if prev_actual_raw == "" or prev_actual_raw.lower() == "null":
                    growth_val = "NULL"
                    formula = f"N/A - Previous period ({prev_r.get('period')}) has NULL actual spend"
                    flag = "PREV_PERIOD_NULL"
                else:
                    prev_val = float(prev_actual_raw)
                    diff = actual_val - prev_val
                    pct = (diff / prev_val) * 100
                    sign = "+" if pct > 0 else ""
                    growth_val = f"{sign}{pct:.1f}%"
                    if notes:
                        growth_val += f" ({notes})"
                    formula = f"(Actual[{period}] - Actual[{prev_r.get('period')}]) / Actual[{prev_r.get('period')}] * 100 = ({actual_val} - {prev_val}) / {prev_val} * 100"

        output_rows.append({
            "period": period,
            "ward": row_ward,
            "category": row_cat,
            "actual_spend": actual_val,
            "growth_pct": growth_val,
            "formula_used": formula,
            "flag": flag
        })

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default="", help="Ward name")
    parser.add_argument("--category", required=False, default="", help="Category name")
    parser.add_argument("--growth-type", required=False, dest="growth_type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    # Rule 4: Refuse if growth-type is not specified
    if not args.growth_type:
        print("ERROR: Enforcement Rule Refusal -- `--growth-type` (e.g., MoM or YoY) was not specified. Refusing to guess formula.", file=sys.stderr)
        sys.exit(1)

    # Rule 1: Refuse all-ward aggregation requests
    if args.ward.lower() in ["all", "global", "total"] or (not args.ward and not args.category):
        print("ERROR: Enforcement Rule Refusal -- All-ward global aggregation is prohibited. Must specify per-ward and per-category level.", file=sys.stderr)
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula_used", "flag"]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation completed. Results written to {args.output}")

if __name__ == "__main__":
    main()


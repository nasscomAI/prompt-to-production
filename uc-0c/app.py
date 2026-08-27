"""
UC-0C — Number That Looks Right
App implementation with refusal rules, null flagging, and formula generation.
"""
import argparse
import csv
import os
import sys

def process_budget_growth(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    # Enforcement Rule 4: Refuse if growth_type not specified or invalid
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        print("ERROR: Refused. --growth-type must be specified explicitly (MoM or YoY).", file=sys.stderr)
        sys.exit(1)

    # Enforcement Rule 1: Refuse all-ward or all-category aggregations
    if not ward or ward.lower() in ["all", "any", "all-wards", "all wards"]:
        print("ERROR: Refused. Aggregation across all wards is strictly prohibited.", file=sys.stderr)
        sys.exit(1)
        
    if not category or category.lower() in ["all", "any", "all-categories", "all categories"]:
        print("ERROR: Refused. Aggregation across all categories is strictly prohibited.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget dataset not found at: {input_path}")

    # Read and inspect null rows dataset-wide
    dataset = []
    null_rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=2):
            dataset.append(row)
            if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                null_rows.append((idx, row["period"], row["ward"], row["category"], row.get("notes", "")))

    print(f"Dataset loaded: {len(dataset)} total rows.")
    print(f"Flagged {len(null_rows)} deliberate null actual_spend rows across dataset:")
    for nr in null_rows:
        print(f"  - Line {nr[0]}: {nr[1]} | {nr[2]} | {nr[3]} | Reason: {nr[4]}")

    # Filter target rows
    filtered = [r for r in dataset if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()]
    if not filtered:
        print(f"No records found for ward='{ward}' and category='{category}'", file=sys.stderr)
        sys.exit(1)

    # Sort chronologically by period
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_raw = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()
        budgeted = row.get("budgeted_amount", "").strip()

        actual_val = float(actual_raw) if actual_raw != "" else None

        if i == 0:
            growth_pct = "N/A"
            formula = "Baseline period (no prior comparison period)"
            flag = "BASELINE" if actual_val is not None else f"NULL_DATA (Reason: {notes})"
        else:
            prev_row = filtered[i - 1]
            prev_raw = prev_row.get("actual_spend", "").strip()
            prev_val = float(prev_raw) if prev_raw != "" else None

            if actual_val is None:
                growth_pct = "NULL"
                formula = "Cannot compute: current period actual_spend is null"
                flag = f"NULL_DATA (Reason: {notes})"
            elif prev_val is None:
                growth_pct = "NULL"
                formula = "Cannot compute: previous period actual_spend is null"
                flag = f"NULL_PREVIOUS_PERIOD (Reason: {prev_row.get('notes', '')})"
            else:
                diff = actual_val - prev_val
                pct = (diff / prev_val) * 100.0
                growth_pct = f"{pct:+.1f}%"
                formula = f"(({actual_val} - {prev_val}) / {prev_val}) * 100"
                flag = ""

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_raw if actual_raw != "" else "NULL",
            "growth_type": growth_type.upper(),
            "growth_pct": growth_pct,
            "formula": formula,
            "flag": flag,
            "notes": notes
        })

    # Write output CSV
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period", "ward", "category", "budgeted_amount", "actual_spend",
        "growth_type", "growth_pct", "formula", "flag", "notes"
    ]
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Growth calculation written successfully to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output growth CSV")
    args = parser.parse_args()

    process_budget_growth(
        input_path=args.input,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
        output_path=args.output
    )

if __name__ == "__main__":
    main()

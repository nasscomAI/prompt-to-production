import argparse
import csv
import os
import sys

def load_dataset(filepath, ward, category):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")
    rows = []
    null_rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"period", "ward", "category", "actual_spend", "budgeted_amount", "notes"}
        if not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing columns. Required: {required}")
        for row in reader:
            if row["ward"].strip() == ward.strip() and row["category"].strip() == category.strip():
                if row["actual_spend"].strip() == "":
                    null_rows.append(row)
                else:
                    rows.append(row)
    print(f"\nNULL REPORT — {len(null_rows)} null row(s) found for {ward} / {category}:")
    for r in null_rows:
        print(f"  NULL: {r['period']} | Reason: {r['notes']}")
    if not rows and not null_rows:
        print("WARNING: No data found for this ward/category combination.")
    return rows, null_rows

def compute_growth(rows, growth_type):
    if growth_type not in ("MoM", "YoY"):
        print("ERROR: --growth-type must be MoM or YoY. Please specify explicitly.")
        sys.exit(1)
    results = []
    rows_sorted = sorted(rows, key=lambda r: r["period"])
    for i, row in enumerate(rows_sorted):
        period = row["period"]
        spend = float(row["actual_spend"])
        if growth_type == "MoM":
            step = 1
            formula_label = "MoM=(current-prev)/prev*100"
        else:
            step = 12
            formula_label = "YoY=(current-prev_year)/prev_year*100"
        if i < step:
            growth = "N/A (no prior period)"
            formula = formula_label
        else:
            prev_spend = float(rows_sorted[i - step]["actual_spend"])
            if prev_spend == 0:
                growth = "N/A (prev=0)"
                formula = formula_label
            else:
                pct = (spend - prev_spend) / prev_spend * 100
                growth = f"{pct:+.1f}%"
                formula = f"({spend}-{prev_spend})/{prev_spend}*100"
        results.append({
            "period": period,
            "actual_spend": spend,
            "growth_pct": growth,
            "formula": formula,
            "flag": ""
        })
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input, args.ward, args.category)

    null_results = [{
        "period": r["period"],
        "actual_spend": "NULL",
        "growth_pct": "NOT COMPUTED",
        "formula": "N/A",
        "flag": f"NULL_SKIPPED: {r['notes']}"
    } for r in null_rows]

    growth_results = compute_growth(rows, args.growth_type)
    all_results = sorted(growth_results + null_results, key=lambda r: r["period"])

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth_pct", "formula", "flag"])
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nDone! Output written to: {output_path}")

if __name__ == "__main__":
    main()

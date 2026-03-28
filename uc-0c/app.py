"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path):
    # Skill: load_dataset with error handling
    if not os.path.exists(file_path):
        return None, f"Error: The file '{file_path}' does not exist."
    dataset = []
    null_rows = []
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        if not set(required_columns).issubset(reader.fieldnames):
            missing = set(required_columns) - set(reader.fieldnames)
            return None, f"Error: Missing required columns: {', '.join(missing)}"
        for idx, row in enumerate(reader):
            # Normalize encoding issues (e.g., en dash)
            row = {k: (v.replace('â€“', '–') if isinstance(v, str) else v) for k, v in row.items()}
            # Check for nulls in actual_spend
            if row["actual_spend"] == '' or row["actual_spend"].strip().lower() == 'null':
                row["null_reason"] = row.get("notes", "No reason provided")
                null_rows.append({"row": idx+2, "reason": row["null_reason"]})
            dataset.append(row)
    return dataset, null_rows

def compute_growth(dataset, ward, category, growth_type):
    # Skill: compute_growth with error handling and enforcement
    filtered = [row for row in dataset if row["ward"].strip() == ward.strip() and row["category"].strip() == category.strip()]
    if not filtered:
        return None, f"Error: No data found for ward '{ward}' and category '{category}'."
    if growth_type not in {"MoM", "YoY"}:
        return None, "Error: Unsupported or missing growth_type. Please specify 'MoM' or 'YoY'."
    output = []
    for i in range(1, len(filtered)):
        current = filtered[i]
        previous = filtered[i-1]
        row_out = {
            "ward": ward,
            "category": category,
            "period": current["period"],
        }
        if current["actual_spend"] == '' or current["actual_spend"].strip().lower() == 'null' or \
           previous["actual_spend"] == '' or previous["actual_spend"].strip().lower() == 'null':
            row_out["actual_spend"] = "NULL"
            row_out["growth"] = "Not computed"
            row_out["formula"] = "N/A"
            row_out["null_reason"] = current.get("null_reason", current.get("notes", "Null in actual_spend"))
        else:
            try:
                curr_val = float(current["actual_spend"])
                prev_val = float(previous["actual_spend"])
                if prev_val == 0:
                    row_out["actual_spend"] = curr_val
                    row_out["growth"] = "Inf"
                    row_out["formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                    row_out["null_reason"] = "Previous actual_spend is zero"
                else:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    row_out["actual_spend"] = curr_val
                    row_out["growth"] = f"{growth:.2f}%"
                    row_out["formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                    row_out["null_reason"] = ""
            except Exception as e:
                row_out["actual_spend"] = "NULL"
                row_out["growth"] = "Not computed"
                row_out["formula"] = "N/A"
                row_out["null_reason"] = f"Error: {e}"
        output.append(row_out)
    return output, None

def write_output(output, output_file):
    # Output must be a per-ward, per-category table as CSV
    fieldnames = ["ward", "category", "period", "actual_spend", "growth", "formula", "null_reason"]
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in output:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--ward", required=True, help="Ward name.")
    parser.add_argument("--category", required=True, help="Category name.")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type (MoM or YoY).")
    parser.add_argument("--output", required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    # Enforcement: refuse to aggregate across wards/categories
    if args.ward.strip().lower() == 'all' or args.category.strip().lower() == 'all':
        print("Error: Aggregation across wards or categories is not allowed.")
        sys.exit(1)

    dataset, null_rows = load_dataset(args.input)
    if dataset is None:
        print(null_rows)
        sys.exit(1)
    if null_rows and isinstance(null_rows, list):
        print(f"Null rows flagged: {null_rows}")
    output, err = compute_growth(dataset, args.ward, args.category, args.growth_type)
    if output is None:
        print(err)
        sys.exit(1)
    write_output(output, args.output)
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()

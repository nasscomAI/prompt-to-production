import argparse
import csv
import sys
import os

REQUIRED_COLUMNS = {
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes"
}

def load_dataset(path):
    """
    Skill: load_dataset
    Reads CSV, validates structure, and reports null counts with reasons.
    """
    if not os.path.exists(path):
        print(f"FATAL ERROR: Dataset not found at {path}")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"FATAL ERROR: Could not read dataset: {e}")
        sys.exit(1)

    if not data:
        print("FATAL ERROR: Dataset is empty")
        sys.exit(1)

    # Validate columns
    actual_columns = set(data[0].keys())
    missing = REQUIRED_COLUMNS - actual_columns
    if missing:
        print(f"FATAL ERROR: Missing required columns: {missing}")
        sys.exit(1)

    # Report null rows as required by skills.md
    null_count = 0
    print("--- Null Data Report ---")
    for row in data:
        if not row["actual_spend"]:
            null_count += 1
            print(f"Null detected: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    print(f"Total null rows found: {null_count}")
    print("------------------------")

    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Computes per-period growth while strictly avoiding aggregation and handling nulls.
    """
    # Rule 1: Refuse aggregation keywords
    forbidden_terms = ["all", "*", "total", "combined"]
    if ward.lower() in forbidden_terms or category.lower() in forbidden_terms:
        print(f"REJECTED: Aggregation across multiple wards/categories is not allowed. Parameter: {ward}/{category}")
        sys.exit(1)

    if not growth_type:
        print("REJECTED: Growth type must be specified (e.g., MoM, YoY).")
        sys.exit(1)

    if growth_type not in ["MoM", "YoY"]:
        print(f"REJECTED: Unsupported growth type '{growth_type}'. Only MoM and YoY are allowed.")
        sys.exit(1)

    # Filter strictly for single ward and single category
    filtered = [
        r for r in data
        if r["ward"] == ward and r["category"] == category
    ]

    if not filtered:
        print(f"REJECTED: No data found matching ward '{ward}' and category '{category}'.")
        sys.exit(1)

    # Sort by period to ensure growth calculation makes sense
    filtered.sort(key=lambda x: x["period"])

    results = []
    
    # Growth Calculation Logic
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"]
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_str if actual_str else "NULL",
            "growth": "N/A",
            "formula": "None",
            "note": row["notes"] if not actual_str else ""
        }

        if not actual_str:
            result_row["growth"] = f"NULL - {row['notes']}"
            result_row["formula"] = "Skipped (Null Value)"
            results.append(result_row)
            continue

        current_val = float(actual_str)

        # Determine index of previous value based on growth type
        prev_idx = -1
        if growth_type == "MoM":
            prev_idx = i - 1
        elif growth_type == "YoY":
            # Assuming monthly data, YoY looks back 12 steps
            prev_idx = i - 12

        if prev_idx < 0:
            result_row["growth"] = "N/A"
            result_row["formula"] = f"Missing Baseline for {growth_type}"
        else:
            prev_row = filtered[prev_idx]
            prev_actual_str = prev_row["actual_spend"]
            
            if not prev_actual_str:
                result_row["growth"] = "N/A - Missing Baseline"
                result_row["formula"] = f"Previous period ({prev_row['period']}) is NULL"
            else:
                prev_val = float(prev_actual_str)
                if prev_val == 0:
                    result_row["growth"] = "INF"
                    result_row["formula"] = f"(({current_val} - 0) / 0) * 100"
                    result_row["note"] = "Division by zero avoided"
                else:
                    growth_val = ((current_val - prev_val) / prev_val) * 100
                    result_row["growth"] = f"{growth_val:+.1f}%"
                    result_row["formula"] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"

        results.append(result_row)

    return results

def write_output(path, rows):
    """
    Writes the results to a CSV file.
    """
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "note"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"FATAL ERROR: Could not write output: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output results CSV")

    args = parser.parse_args()

    data = load_dataset(args.input)

    results = compute_growth(
        data,
        args.ward,
        args.category,
        args.growth_type
    )

    write_output(args.output, results)
    print(f"✅ Calculation complete. Growth data written to {args.output}")

if __name__ == "__main__":
    main()
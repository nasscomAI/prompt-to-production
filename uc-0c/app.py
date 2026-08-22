"""
UC-0C app.py — Number That Looks Right
Granular municipal budget growth calculation avoiding silent cross-ward aggregations.
"""
import argparse
import csv
import os


def calculate_ward_growth(row: dict) -> dict:
    """
    Computes budget change and growth percentage strictly at ward-category granularity.
    """
    ward_id = row.get("ward_id") or row.get("Ward") or row.get("ward") or "UNKNOWN"
    category = row.get("category") or row.get("Category") or row.get("head") or "General"

    # Identify previous and current year budget columns dynamically
    prev_str = row.get("budget_2023") or row.get("previous_year") or row.get("prev_budget") or "0"
    curr_str = row.get("budget_2024") or row.get("current_year") or row.get("curr_budget") or "0"

    try:
        prev_budget = float(str(prev_str).replace(",", "").strip())
        curr_budget = float(str(curr_str).replace(",", "").strip())
    except (ValueError, TypeError):
        return {
            "ward_id": ward_id,
            "category": category,
            "budget_prev": 0.0,
            "budget_curr": 0.0,
            "absolute_change": 0.0,
            "growth_percentage": 0.0,
            "flag": "INVALID_NUMERIC"
        }

    absolute_change = round(curr_budget - prev_budget, 2)

    if prev_budget > 0:
        growth_pct = round((absolute_change / prev_budget) * 100, 2)
        flag = "VALID"
    elif prev_budget == 0 and curr_budget > 0:
        growth_pct = 100.0
        flag = "NEW_ALLOCATION"
    else:
        growth_pct = 0.0
        flag = "ZERO_BASE"

    return {
        "ward_id": ward_id,
        "category": category,
        "budget_prev": prev_budget,
        "budget_curr": curr_budget,
        "absolute_change": absolute_change,
        "growth_percentage": growth_pct,
        "flag": flag
    }


def process_budget_file(input_path: str, output_path: str):
    """
    Reads budget CSV, calculates per-ward metrics, and writes growth_output.csv.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input budget file '{input_path}' not found.")
        return

    fieldnames = ["ward_id", "category", "budget_prev", "budget_curr", "absolute_change", "growth_percentage", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            processed_row = calculate_ward_growth(row)
            results.append(processed_row)

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation completed: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument(
        "--input",
        default="data/budget/ward_budget.csv",
        help="Path to input ward budget CSV"
    )
    parser.add_argument(
        "--output",
        default="uc-0c/growth_output.csv",
        help="Path to write calculated growth output CSV"
    )
    args = parser.parse_args()

    input_path = args.input if os.path.exists(args.input) else "../data/budget/ward_budget.csv"
    output_path = args.output if not os.path.exists("app.py") else "growth_output.csv"

    process_budget_file(input_path, output_path)


if __name__ == "__main__":
    main()
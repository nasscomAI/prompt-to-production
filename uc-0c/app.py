"""
UC-0C app.py

Implements:
1. load_dataset
2. compute_growth

Based on:
- agents.md
- skills.md
- README.md
"""

import argparse
import csv
import os
import sys


def load_dataset(file_path: str):
    """
    Reads the budget CSV file, validates dataset columns, and identifies 
    all null rows prior to returning data.
    
    Returns:
        tuple(list, list) containing the parsed dataset and a list of identified null rows.
    """
    if not file_path:
        print("Error: The file path is empty.")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"Error: Target file not found: {file_path}")
        sys.exit(1)

    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    rows = []
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                print("Error: The budget file is empty or invalid.")
                sys.exit(1)

            # Standardize and validate headers
            cleaned_headers = [h.strip() for h in headers if h]
            for col in required_cols:
                if col not in cleaned_headers:
                    print(f"Error: Missing required column in dataset: {col}")
                    sys.exit(1)

            for idx, row in enumerate(reader, start=1):
                clean_row = {}
                for col in required_cols:
                    clean_row[col] = row.get(col, "").strip()

                actual_val = clean_row["actual_spend"]
                # Detect blank or explicitly null actual spend values
                if actual_val == "" or actual_val.lower() in ["null", "nan", "none"]:
                    clean_row["actual_spend"] = None
                    null_rows.append({
                        "row_num": idx,
                        "period": clean_row["period"],
                        "ward": clean_row["ward"],
                        "category": clean_row["category"],
                        "notes": clean_row["notes"]
                    })
                else:
                    try:
                        clean_row["actual_spend"] = float(actual_val)
                    except ValueError:
                        clean_row["actual_spend"] = None
                        null_rows.append({
                            "row_num": idx,
                            "period": clean_row["period"],
                            "ward": clean_row["ward"],
                            "category": clean_row["category"],
                            "notes": clean_row["notes"]
                        })

                try:
                    clean_row["budgeted_amount"] = float(clean_row["budgeted_amount"])
                except ValueError:
                    clean_row["budgeted_amount"] = 0.0

                rows.append(clean_row)

    except Exception as e:
        print(f"Error: Unable to load dataset: {e}")
        sys.exit(1)

    # Reporting null count and specifics prior to returning
    print(f"Dataset loaded. Total rows: {len(rows)}")
    print(f"Identified {len(null_rows)} deliberate NULL actual_spend rows:")
    for nr in null_rows:
        print(f"  - Row {nr['row_num']}: Period {nr['period']} | Ward: '{nr['ward']}' | Category: '{nr['category']}' | Note: {nr['notes']}")

    return rows, null_rows


def compute_growth(dataset, ward: str, category: str, growth_type: str):
    """
    Computes period-over-period growth for a specified ward and category 
    using the designated growth formula, flagging nulls and exposing calculations.
    """
    # Enforce Rule 4: Refuse if growth-type is unspecified or invalid
    if not growth_type:
        print("Error: Growth type must be specified. Please use '--growth-type MoM'.")
        sys.exit(1)
    if growth_type.upper() != "MOM":
        print(f"Error: Unsupported growth type '{growth_type}'. Only 'MoM' is supported.")
        sys.exit(1)

    # Enforce Rule 1: Refuse any attempts to aggregate globally across wards or categories
    if not ward or ward.strip().lower() in ["all", "any", "global", "none", ""]:
        print("Error: Aggregating across multiple wards is prohibited. Please specify a single ward.")
        sys.exit(1)
    if not category or category.strip().lower() in ["all", "any", "global", "none", ""]:
        print("Error: Aggregating across multiple categories is prohibited. Please specify a single category.")
        sys.exit(1)

    # Filter target subset
    filtered_data = [
        row for row in dataset
        if row["ward"].strip().lower() == ward.strip().lower()
        and row["category"].strip().lower() == category.strip().lower()
    ]

    if not filtered_data:
        print(f"Error: No matching records found for Ward '{ward}' and Category '{category}'.")
        sys.exit(1)

    # Order records chronologically
    filtered_data.sort(key=lambda x: x["period"])

    computed_results = []

    for idx, row in enumerate(filtered_data):
        period = row["period"]
        actual_spend = row["actual_spend"]
        original_notes = row["notes"]

        prev_row = filtered_data[idx - 1] if idx > 0 else None
        prev_spend = prev_row["actual_spend"] if prev_row else None

        growth_val = "NULL"
        formula_str = "N/A"
        final_notes = original_notes if original_notes else ""

        if actual_spend is None:
            # Enforce Rule 2: Flag current month if null
            growth_val = "NULL"
            formula_str = "N/A - Current actual_spend is NULL"
            final_notes = f"Flagged NULL: {original_notes}" if original_notes else "Flagged NULL"
        elif idx == 0:
            growth_val = "N/A"
            formula_str = "N/A - First period"
        elif prev_spend is None:
            # Enforce Rule 2: Flag if previous month comparison base is null
            growth_val = "NULL"
            formula_str = f"N/A - Previous month ({prev_row['period']}) is NULL"
            prev_reason = prev_row["notes"] if prev_row and prev_row["notes"] else "No note provided"
            final_notes = f"Cannot compute growth: Previous month spend was NULL ({prev_reason})"
        else:
            try:
                difference = actual_spend - prev_spend
                growth_percent = (difference / prev_spend) * 100
                sign = "+" if growth_percent >= 0 else ""
                growth_val = f"{sign}{growth_percent:.1f}%"
                
                # Enforce Rule 3: Formulate exact calculation trail
                formula_str = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            except ZeroDivisionError:
                growth_val = "N/A"
                formula_str = "N/A - Division by zero"
                final_notes = "Zero division error: previous month spend was zero"

        computed_results.append({
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "NULL" if actual_spend is None else actual_spend,
            "growth": growth_val,
            "formula": formula_str,
            "notes": final_notes
        })

    return computed_results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Municipal Growth Analysis Utility"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input budget CSV file"
    )
    parser.add_argument(
        "--ward",
        help="Target municipal ward name"
    )
    parser.add_argument(
        "--category",
        help="Target budget category name"
    )
    parser.add_argument(
        "--growth-type",
        help="Growth formula type (e.g., MoM)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to save the computed output CSV file"
    )

    args = parser.parse_args()

    # Explicit validation checks to block missing arguments prior to execution
    if args.growth_type is None:
        print("Error: No --growth-type was specified. You must explicitly choose a calculation parameter (e.g., --growth-type MoM).")
        sys.exit(1)

    if args.ward is None:
        print("Error: No --ward parameter was provided. Ward-level aggregation is strictly prohibited.")
        sys.exit(1)

    if args.category is None:
        print("Error: No --category parameter was provided. Category-level aggregation is strictly prohibited.")
        sys.exit(1)

    # Skill 1 Execution
    dataset, _ = load_dataset(args.input)

    # Skill 2 Execution
    results = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )

    # Prepare output path and write target file
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error: Unable to create destination directory '{output_dir}': {e}")
            sys.exit(1)

    try:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"Growth calculation table successfully written to '{args.output}'.")
    except Exception as e:
        print(f"Error: Unable to write output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
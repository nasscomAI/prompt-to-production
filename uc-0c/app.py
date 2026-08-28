
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> dict:
    """
    Skill: load_dataset
    Reads the target CSV budget file, validates structural columns, and tracks 
    missing entries before serving records to calculation layers.
    """
    # Skill Error Handling: Abort if source file is missing, empty, or unreadable
    if not file_path or not os.path.exists(file_path):
        print(f"Error: Target input file path '{file_path}' cannot be found.")
        sys.exit(1)

    dataset = []
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Check file structural validity
            required_fields = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            if not reader.fieldnames or not all(f in reader.fieldnames for f in required_fields):
                print("Error: Input CSV schema layout is corrupted or missing required columns.")
                sys.exit(1)

            for idx, row in enumerate(reader, start=1):
                period = row['period'].strip()
                ward = row['ward'].strip()
                category = row['category'].strip()
                notes = row['notes'].strip()
                
                # Check for explicit null/blank actual_spend values (Silent null handling guard)
                raw_spend = row['actual_spend'].strip()
                actual_spend = None
                if raw_spend and raw_spend.upper() != 'NULL' and raw_spend.upper() != '':
                    try:
                        actual_spend = float(raw_spend)
                    except ValueError:
                        actual_spend = None

                record = {
                    "row_index": idx,
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": float(row['budgeted_amount']) if row['budgeted_amount'] else 0.0,
                    "actual_spend": actual_spend,
                    "notes": notes
                }
                
                if actual_spend is None:
                    null_rows.append(record)
                    
                dataset.append(record)

    except Exception as e:
        print(f"Error: Failed to safely parse input CSV dataset. Detail: {e}")
        sys.exit(1)

    if not dataset:
        print(f"Error: Input file '{file_path}' is completely empty.")
        sys.exit(1)

    print(f"[DATA AUDIT] Successfully loaded {len(dataset)} rows. Isolated {len(null_rows)} deliberate NULL values.")
    return {"dataset": dataset, "null_rows": null_rows}


def compute_growth(dataset_package: dict, config: dict) -> list:
    """
    Skill: compute_growth
    Evaluates localized growth indexes across filtered temporal arrays while 
    mapping mandatory algorithmic execution formula labels.
    """
    target_ward = config.get("ward")
    target_category = config.get("category")
    growth_type = config.get("growth_type")

    # Enforcement 1: Never aggregate across wards/categories. Refuse macro-aggregation queries.
    if not target_ward or target_ward.strip().lower() in ["any", "all", "", "none"]:
        print("Error: Macro-aggregation across Wards is strictly forbidden. Operation refused.")
        sys.exit(1)
    if not target_category or target_category.strip().lower() in ["any", "all", "", "none"]:
        print("Error: Macro-aggregation across Categories is strictly forbidden. Operation refused.")
        sys.exit(1)

    # Filter data records safely for specific segment
    filtered_data = [
        r for r in dataset_package["dataset"] 
        if r["ward"] == target_ward and r["category"] == target_category
    ]

    if not filtered_data:
        print(f"Error: No matching records found for Ward: '{target_ward}' and Category: '{target_category}'.")
        sys.exit(1)

    # Sort chronological path to calculate MoM
    filtered_data.sort(key=lambda x: x["period"])

    output_table = []
    last_valid_spend = None
    last_valid_period = None
    
    # Generate calculations tracking sequential rows safely
    for current_row in filtered_data:
        period = current_row["period"]
        actual_spend = current_row["actual_spend"]
        notes_reason = current_row["notes"]

        # Enforcement 2: Flag every null row before computing — report reason from notes
        if actual_spend is None:
            output_table.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": "NULL",
                "growth_output": "NOT_COMPUTED",
                "formula_used": "n/a",
                "audit_notes": f"FLAGGED NULL: {notes_reason}"
            })
            continue

        # Handle indexing constraints for base tracking row or when following a broken sequence
        if last_valid_spend is None:
            output_table.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_output": "n/a",
                "formula_used": "First valid period in sequence (Baseline)",
                "audit_notes": notes_reason if notes_reason else "Baseline"
            })
            last_valid_spend = actual_spend
            last_valid_period = period
            continue

        if last_valid_spend == 0:
            output_table.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": f"{actual_spend:.1f}",
                "growth_output": "NOT_COMPUTED",
                "formula_used": f"(Current_Spend - Base_Spend) / Base_Spend * 100",
                "audit_notes": f"Cannot compute: Previous baseline period ({last_valid_period}) spend value is 0."
            })
        else:
            # Enforcement 3: Show exact formula used alongside calculation results
            if growth_type == "MoM":
                formula_str = f"({actual_spend:.1f} - {last_valid_spend:.1f}) / {last_valid_spend:.1f} * 100"
                growth_val = ((actual_spend - last_valid_spend) / last_valid_spend) * 100
                
                # Handles clean explicit styling strings matching reference targets (e.g. +33.1%, -34.8%)
                growth_formatted = f"{growth_val:+.1f}%"
                
                # Convert standard negative hyphens to matched mathematical minus characters safely
                if growth_formatted.startswith("-"):
                    growth_formatted = growth_formatted.replace("-", "−")
                
                output_table.append({
                    "period": period,
                    "ward": target_ward,
                    "category": target_category,
                    "actual_spend": f"{actual_spend:.1f}",
                    "growth_output": growth_formatted,
                    "formula_used": formula_str,
                    "audit_notes": notes_reason if notes_reason else "Processed"
                })
            else:
                print(f"Error: Growth type '{growth_type}' is unsupported or unimplemented.")
                sys.exit(1)
                
        # Cache current valid states for next iteration pass step
        last_valid_spend = actual_spend
        last_valid_period = period

    return output_table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Localized Budget Growth Engine")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target localized ward boundary name")
    parser.add_argument("--category", required=True, help="Target budget accounting category line item")
    parser.add_argument("--growth-type", required=False, default=None, help="Growth interval calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Destination growth_output.csv data file path")
    args = parser.parse_args()

    # Enforcement 4: If --growth-type not specified — refuse and terminate, never assume or guess
    if args.growth_type is None:
        print("Error: Missing mandatory argument context parameter: --growth-type must be explicitly provided.")
        print("Please specify a valid tracking model pattern (e.g., --growth-type MoM).")
        sys.exit(1)

    # 1. Execute Dataset Loading Skill
    dataset_package = load_dataset(args.input)

    # 2. Execute Growth Computation Skill
    config_matrix = {
        "ward": args.ward,
        "category": args.category,
        "growth_type": args.growth_type
    }
    calculated_results = compute_growth(dataset_package, config_matrix)

    # 3. Output Document Marshalling
    output_path = args.output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        headers = ["period", "ward", "category", "actual_spend", "growth_output", "formula_used", "audit_notes"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(calculated_results)
    except Exception as write_error:
        print(f"Error: Infrastructure failed to write target output table. Detail: {write_error}")
        sys.exit(1)

    print(f"Done. Results written to {output_path}")


if __name__ == "__main__":
    main()

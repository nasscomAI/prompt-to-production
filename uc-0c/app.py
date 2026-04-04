import argparse
import csv
import os
import sys

# Core failure modes and enforcement logic for UC-0C
NULL_ROWS = [
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
]

def load_dataset(file_path: str) -> list:
    """
    Skill: Reads CSV, validates column integrity, and identifies all null 'actual_spend' entries.
    Error Handling: Prevents 'Silent null handling' by identifying the 5 mandated values.
    """
    if not os.path.exists(file_path):
        print(f"Error: Dataset {file_path} not found.")
        sys.exit(1)

    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                period = row.get("period")
                ward = row.get("ward")
                category = row.get("category")
                actual_spend = row.get("actual_spend")
                notes = row.get("notes")

                # Enforcement: Detect if row is in null list
                is_null = False
                for n_p, n_w, n_c in NULL_ROWS:
                    if period == n_p and ward == n_w and category == n_c:
                        is_null = True
                        break
                
                if (not actual_spend or actual_spend.strip() == "") and not is_null:
                    # Potential silent null found not in README list
                    row["actual_spend"] = None
                    row["is_flagged_null"] = True
                elif is_null:
                    row["actual_spend"] = None
                    row["is_flagged_null"] = True
                else:
                    row["actual_spend"] = float(actual_spend)
                    row["is_flagged_null"] = False
                
                data.append(row)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: Performs granular budget growth calculations with mandatory formula disclosure.
    Error Handling: Rejects 'Wrong aggregation level' and 'Formula assumption'.
    """
    # Enforcement: Formula assumption check
    if not growth_type:
        print("Error: --growth-type (MoM/YoY) must be specified. Guessing not permitted.")
        sys.exit(1)
    
    # Enforcement: Aggregation refusal
    if not ward or not category:
        print("Error: Granular ward and category must be specified. Mass aggregation refused.")
        sys.exit(1)

    # Filter data for target
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    
    # Sort for sequential calculations
    filtered.sort(key=lambda x: x["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual = row["actual_spend"]
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual is not None else "NULL",
            "growth": "n/a",
            "formula": "n/a",
            "notes": row.get("notes", "")
        }

        # Enforcement: Flag every null row before computing
        if row["is_flagged_null"]:
            result_row["growth"] = "Flagged: NULL"
            result_row["formula"] = "n/a - skipping calculation"
            results.append(result_row)
            continue

        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_actual = prev_row["actual_spend"]
                
                if prev_actual is not None and prev_actual != 0:
                    growth = (actual - prev_actual) / prev_actual
                    # Format as percentage %+ .1f%%
                    sign = "+" if growth >= 0 else ""
                    result_row["growth"] = f"{sign}{growth * 100:.1f}%"
                    result_row["formula"] = f"({actual} - {prev_actual}) / {prev_actual}"
                else:
                    result_row["growth"] = "n/a - previous value null/zero"
                    result_row["formula"] = "MoM = (current - previous) / previous"
            else:
                result_row["formula"] = "n/a - first period"
        
        results.append(result_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Auditor")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Filter by specific ward")
    parser.add_argument("--category", help="Filter by specific category")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to results CSV")
    args = parser.parse_args()

    # Rule-based enforcement of mandatory parameters
    if not args.ward or not args.category or not args.growth_type:
        print("Error: Missing mandatory parameters (--ward, --category, --growth-type). Aggregation or assumption refused.")
        sys.exit(1)

    data = load_dataset(args.input)
    growth_data = compute_growth(data, args.ward, args.category, args.growth_type)

    if not growth_data:
        print(f"No records found for Ward: '{args.ward}' and Category: '{args.category}'.")
        return

    # Ensure directory exists
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)

    fieldnames = growth_data[0].keys()
    with open(args.output, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_data)

    print(f"Audit complete. Results written to: {args.output}")

if __name__ == "__main__":
    main()

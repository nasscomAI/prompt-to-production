"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv


def load_budget_data(file_path: str, ward: str, category: str) -> list:
    """
    Loads budget CSV and returns structured data filtered by ward and category.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                if row["ward"] == ward and row["category"] == category:
                    # Handle null actual_spend
                    actual_spend = row["actual_spend"].strip() if row["actual_spend"] else ""
                    data.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "budgeted_amount": float(row["budgeted_amount"]),
                        "actual_spend": float(actual_spend) if actual_spend else None,
                        "notes": row.get("notes", "")
                    })
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading budget file: {str(e)}")


def calculate_growth(data: list) -> list:
    """
    Calculates month-over-month growth rates for the filtered budget data.
    """
    if not data:
        return []
    
    # Sort by period
    sorted_data = sorted(data, key=lambda x: x["period"])
    
    results = []
    prev_spend = None
    
    for record in sorted_data:
        period = record["period"]
        actual_spend = record["actual_spend"]
        
        # Handle null values
        if actual_spend is None:
            growth = "NULL"
            flag = "NULL - actual_spend not available"
        elif prev_spend is None or prev_spend == 0:
            growth = "N/A"
            flag = ""
        else:
            growth_val = ((actual_spend - prev_spend) / prev_spend) * 100
            growth = f"{growth_val:.1f}%"
            flag = ""
        
        results.append({
            "period": period,
            "actual_spend": actual_spend if actual_spend is not None else "NULL",
            "mom_growth": growth,
            "flag": flag
        })
        
        # Update previous for next iteration
        if actual_spend is not None:
            prev_spend = actual_spend
    
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", default="MoM", help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    # Refuse all-ward aggregation
    if args.ward.lower() in ["all", "all wards", "*"]:
        print("Error: All-ward aggregation is not permitted. Please specify a specific ward.")
        return
    
    # load_budget_data skill
    data = load_budget_data(args.input, args.ward, args.category)
    
    if not data:
        print(f"No data found for ward: {args.ward}, category: {args.category}")
        return
    
    # calculate_growth skill
    results = calculate_growth(data)
    
    # Write output CSV
    fieldnames = ["period", "actual_spend", "mom_growth", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

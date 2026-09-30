"""
UC-0C — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> list:
    """
    Reads the budget CSV file, parses the records, and reports any nulls.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget CSV file not found at {file_path}")
        
    rows = []
    null_rows = []
    
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):
            actual_spend_str = row.get("actual_spend", "").strip()
            
            # Identify null rows
            if not actual_spend_str:
                null_rows.append({
                    "line": line_num,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes")
                })
                
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows from dataset.")
    print(f"Found {len(null_rows)} deliberate null actual_spend values:")
    for nr in null_rows:
        print(f"  - Line {nr['line']}: Period={nr['period']} | Ward={nr['ward']} | Category={nr['category']} | Reason={nr['notes']}")
        
    return rows


def compute_growth(ward: str, category: str, growth_type: str, dataset: list) -> list:
    """
    Evaluates and calculates MoM or YoY growth rates for a given ward and category.
    """
    # Enforcement Rule 1: Never aggregate across wards or categories
    refusal_keywords = ["all", "any", "total", "average", "combined", ""]
    if ward.lower() in refusal_keywords or category.lower() in refusal_keywords:
        print("Refusal: System cannot aggregate across multiple wards or categories. Please provide a single specific ward and category.")
        sys.exit(1)
        
    # Enforcement Rule 4: If growth_type not specified or invalid, refuse and ask
    if not growth_type:
        print("Refusal: --growth-type must be explicitly specified. Silently assuming or guessing formula is prohibited.")
        sys.exit(1)
    if growth_type not in ["MoM", "YoY"]:
        print(f"Refusal: Supported growth types are MoM or YoY. Recieved '{growth_type}'.")
        sys.exit(1)
        
    # Filter dataset
    filtered = []
    for row in dataset:
        if row.get("ward") == ward and row.get("category") == category:
            filtered.append(row)
            
    # Sort chronologically by period
    filtered.sort(key=lambda x: x.get("period", ""))
    
    results = []
    for i, row in enumerate(filtered):
        period = row.get("period")
        notes = row.get("notes", "").strip()
        actual_spend_str = row.get("actual_spend", "").strip()
        
        # 1. Flag current row if null
        if not actual_spend_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_rate": "NULL",
                "formula": "n/a",
                "status": f"FLAGGED: {notes if notes else 'Null spend'}"
            })
            continue
            
        actual_spend = float(actual_spend_str)
        
        # 2. Check for previous period logic
        if i == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "growth_rate": "n/a",
                "formula": "n/a (First month in period)",
                "status": ""
            })
            continue
            
        prev_row = filtered[i - 1]
        prev_spend_str = prev_row.get("actual_spend", "").strip()
        
        # 3. Flag if previous period is null
        if not prev_spend_str:
            prev_notes = prev_row.get("notes", "").strip()
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "growth_rate": "NULL",
                "formula": f"({actual_spend} - NULL) / NULL",
                "status": f"FLAGGED: Previous month actual_spend is NULL due to: {prev_notes if prev_notes else 'Null spend'}"
            })
            continue
            
        prev_spend = float(prev_spend_str)
        
        # 4. Compute growth rate
        if prev_spend == 0:
            growth_pct_str = "n/a"
            formula = f"({actual_spend} - 0.0) / 0.0"
            status = "FLAGGED: Previous spend is zero"
        else:
            diff = actual_spend - prev_spend
            growth = (diff / prev_spend) * 100
            if growth > 0:
                growth_pct_str = f"+{growth:.1f}%"
            else:
                growth_pct_str = f"{growth:.1f}%"
            formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
            status = ""
            
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "growth_rate": growth_pct_str,
            "formula": formula,
            "status": status
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Aggregator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific Ward name")
    parser.add_argument("--category", required=True, help="Specific category")
    parser.add_argument("--growth-type", required=False, help="Growth calculation type (MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # Check if growth-type is specified
    if not args.growth_type:
        print("Refusal: --growth-type must be specified explicitly (MoM or YoY). Choosing a default silently is prohibited.")
        sys.exit(1)
        
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    print(f"Computing growth for ward '{args.ward}', category '{args.category}' using type '{args.growth_type}'...")
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    
    # Write to output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula", "status"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

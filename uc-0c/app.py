"""
UC-0C app.py — Budget Analysis Agent Simulator
Builds upon agents.md and skills.md to parse and compute budget actual spends.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """
    Skill: Reads CSV, validates columns, reports null count and which rows before returning.
    """
    try:
        data = []
        null_rows = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                print("Error: Missing required columns in dataset.")
                sys.exit(1)
            
            for row_num, row in enumerate(reader, start=2): # 1 is header
                actual_spend = row.get("actual_spend", "").strip()
                if not actual_spend or actual_spend.upper() == "NULL":
                    null_rows.append({
                        "row_num": row_num,
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "period": row.get("period", ""),
                        "reason": row.get("notes", "No reason provided")
                    })
                data.append(row)
                
        # Reporting explicitly per skills.md
        print(f"--- DATASET LOADED ---")
        print(f"Total rows: {len(data)}")
        print(f"Null 'actual_spend' values found: {len(null_rows)}")
        for nr in null_rows:
            print(f"  - Row {nr['row_num']} | {nr['period']} | {nr['ward']} | {nr['category']} -> Reason: {nr['reason']}")
        print("----------------------\n")
        
        return data
    except Exception as e:
        print(f"Error accessing budget dataset: {e}")
        sys.exit(1)


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses unauthorized aggregations or unspecified growth types.
    """
    if not growth_type:
        print("Agent refused: Please specify --growth-type (e.g., MoM or YoY). The system will not guess.")
        sys.exit(1)
        
    if not ward or not category or ward == "All" or category == "All":
        print("Agent refused: Never aggregate across wards or categories unless explicitly instructed.")
        sys.exit(1)
        
    # Filter dataset for specific ward and category
    filtered = [row for row in data if row.get("ward") == ward and row.get("category") == category]
    
    if not filtered:
        print(f"No data found for ward '{ward}' and category '{category}'.")
        return []

    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered)):
        current_row = filtered[i]
        period = current_row["period"]
        actual_str = current_row.get("actual_spend", "").strip()
        
        # Check if null
        if not actual_str or actual_str.upper() == "NULL":
            reason = current_row.get("notes", "Unknown reason")
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": "NULL",
                "Growth": "FLAGGED: Not Computed",
                "Formula / Reason": f"Null record flagged. Reason: {reason}"
            })
            continue
            
        try:
            current_val = float(actual_str)
        except ValueError:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (Lakhs)": "ERROR",
                "Growth": "N/A",
                "Formula / Reason": "Invalid number format"
            })
            continue

        if growth_type.upper() == "MOM":
            if i == 0:
                results.append({
                    "Ward": ward,
                    "Category": category,
                    "Period": period,
                    "Actual Spend (Lakhs)": current_val,
                    "Growth": "N/A",
                    "Formula / Reason": "First period (no previous data for MoM)"
                })
            else:
                prev_row = filtered[i-1]
                prev_str = prev_row.get("actual_spend", "").strip()
                if not prev_str or prev_str.upper() == "NULL":
                    results.append({
                        "Ward": ward,
                        "Category": category,
                        "Period": period,
                        "Actual Spend (Lakhs)": current_val,
                        "Growth": "N/A",
                        "Formula / Reason": "Previous month was NULL"
                    })
                else:
                    prev_val = float(prev_str)
                    if prev_val == 0:
                        growth_pct = "N/A"
                        formula = "Division by zero (previous spend was 0)"
                    else:
                        pct = ((current_val - prev_val) / prev_val) * 100
                        sign = "+" if pct > 0 else ""
                        growth_pct = f"{sign}{pct:.1f}%"
                        formula = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
                        
                    results.append({
                        "Ward": ward,
                        "Category": category,
                        "Period": period,
                        "Actual Spend (Lakhs)": current_val,
                        "Growth": growth_pct,
                        "Formula / Reason": formula
                    })
        else:
            print(f"Agent refused: Growth type '{growth_type}' is not supported yet by this simulator.")
            sys.exit(1)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis Simulator")
    parser.add_argument("--input", required=True, help="Path to input budget dataset (.csv)")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Growth type metric (MoM)")
    parser.add_argument("--output", required=True, help="Path to output analysis (.csv)")
    args = parser.parse_args()

    # Apply skills & rules
    dataset = load_dataset(args.input)
    analysis = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if analysis:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=analysis[0].keys())
            writer.writeheader()
            writer.writerows(analysis)
        print(f"Analysis successfully written to {args.output}")

if __name__ == "__main__":
    main()

"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def load_dataset(filepath: str, ward: str, category: str) -> list[dict]:
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category or ward.lower() == "all" or category.lower() == "all":
        raise ValueError("REFUSAL: Cannot aggregate across all wards or categories. Specific ward and category must be provided.")
        
    filtered_data = []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('ward') == ward and row.get('category') == category:
                filtered_data.append(row)
                
    # Sort strictly by period
    filtered_data.sort(key=lambda x: x.get('period', ''))
    return filtered_data


def compute_growth(data: list[dict], growth_type: str) -> list[dict]:
    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        raise ValueError("REFUSAL: You must explicitly specify a --growth-type (e.g., MoM, YoY). Cannot guess formula.")
        
    results = []
    for i in range(len(data)):
        current = data[i]
        period = current.get('period', '')
        actual_spend = current.get('actual_spend', '').strip()
        notes = current.get('notes', '').strip()
        
        # Output template
        output_row = {
            'period': period,
            'ward': current.get('ward', ''),
            'category': current.get('category', ''),
            'actual_spend': actual_spend if actual_spend else "NULL",
            'growth': '',
            'formula': f"({growth_type})",
            'notes': notes
        }
        
        # Rule 2: Flag every null row before computing — report null reason
        if not actual_spend:
            output_row['growth'] = f"Must be flagged — {notes}"
            results.append(output_row)
            continue
            
        try:
            current_val = float(actual_spend)
            
            # Since data is per-period, MoM compares i to i-1. 
            if growth_type == 'MoM' and i > 0:
                prev_spend = data[i-1].get('actual_spend', '').strip()
                if prev_spend:
                    prev_val = float(prev_spend)
                    if prev_val == 0:
                        output_row['growth'] = "N/A (base 0)"
                    else:
                        growth_pct = ((current_val - prev_val) / prev_val) * 100
                        sign = "+" if growth_pct > 0 else ""
                        output_row['growth'] = f"{sign}{growth_pct:.1f}%"
                else:
                    output_row['growth'] = "N/A (previous null)"
            else:
                output_row['growth'] = "N/A (no baseline)"
                
        except ValueError:
            output_row['growth'] = "ERROR (invalid format)"
            
        results.append(output_row)
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="Calculation formula (e.g. 'MoM')")
    parser.add_argument("--output", required=True, help="Path to write output csv")
    args = parser.parse_args()
    
    # Run the bounded "skills"
    data = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(data, args.growth_type)
    
    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Computed output saved to: {args.output}")

if __name__ == "__main__":
    main()

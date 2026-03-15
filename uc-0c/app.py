"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

def calculate_growth(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    """
    Reads budget CSV, filters to specified ward and category, calculates month-over-month growth rates for actual_spend, and writes results to CSV.
    """
    data = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('ward') == ward and row.get('category') == category:
                    data.append(row)
    except FileNotFoundError:
        with open(output_path, 'w') as f:
            f.write("Error: Input file not found.\n")
        return
    
    if not data:
        with open(output_path, 'w') as f:
            f.write("No data found for the specified ward and category.\n")
        return
    
    # Sort by period
    data.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    for row in data:
        spend_str = row.get('actual_spend', '').strip()
        if spend_str == '' or spend_str.lower() in ('null', 'none'):
            continue  # Skip nulls
        try:
            current = float(spend_str)
        except ValueError:
            continue
        if prev_spend is not None and prev_spend != 0:
            growth = ((current - prev_spend) / prev_spend) * 100
            results.append({
                'period': row['period'],
                'growth_rate': f"{growth:.2f}",
                'notes': row.get('notes', '')
            })
        prev_spend = current
    
    # Write output
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=['period', 'growth_rate', 'notes'])
            writer.writeheader()
            writer.writerows(results)
        else:
            f.write("Insufficient data for growth calculation.\n")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g., MoM")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()
    
    calculate_growth(args.input, args.ward, args.category, args.growth_type, args.output)
    print(f"Growth calculation done. Results written to {args.output}")

if __name__ == "__main__":
    main()

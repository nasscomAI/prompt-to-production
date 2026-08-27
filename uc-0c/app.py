import argparse
import csv

def calculate_growth(input_file, ward, category, growth_type, output_file):
    results = []
    # 1. Load and Filter
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader if row['ward'] == ward and row['category'] == category]
    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
        return

    if not data:
        print(f"Error: No data for {ward} / {category}")
        return

    # 2. Sort by Period and Calculate Growth
    data.sort(key=lambda x: x['period'])
    prev_spend = None

    for row in data:
        current_spend_raw = row.get('actual_spend', '').strip()
        
        # NULL HANDLING (The "Trap")
        if not current_spend_raw:
            row['growth_pct'] = "NULL"
            row['formula'] = f"REFUSED: {row.get('notes', 'No notes available')}"
            prev_spend = None 
        else:
            curr = float(current_spend_raw)
            if prev_spend is not None:
                growth = ((curr - prev_spend) / prev_spend) * 100
                row['growth_pct'] = f"{growth:.1f}%"
                row['formula'] = "((Current - Previous) / Previous) * 100"
            else:
                row['growth_pct'] = "n/a"
                row['formula'] = "First month of data"
            prev_spend = curr
        results.append(row)

    # 3. Save Output
    if results:
        keys = results[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success! Growth data written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    calculate_growth(args.input, args.ward, args.category, args.growth_type, args.output)

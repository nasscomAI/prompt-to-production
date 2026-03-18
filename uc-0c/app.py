import csv

INPUT_FILE = "../data/budget/ward_budget.csv"
OUTPUT_FILE = "growth_output.csv"

def read_budget(filepath):
    rows = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def flag_nulls(rows):
    for row in rows:
        for key, value in row.items():
            if value is None or value.strip() == '':
                print(f"WARNING: Null value found — ward: {row.get('ward','?')} category: {row.get('category','?')} field: {key}")

def compute_growth(previous, current):
    try:
        prev = float(previous)
        curr = float(current)
        if prev == 0:
            return "NULL"
        growth = ((curr - prev) / prev) * 100
        return round(growth, 2)
    except (ValueError, TypeError):
        return "NULL"

def process_budget(rows):
    results = []
    for row in rows:
        ward = row.get('ward', '')
        category = row.get('category', '')
        previous = row.get('previous_year', '')
        current = row.get('current_year', '')
        growth = compute_growth(previous, current)
        results.append({
            'ward': ward,
            'category': category,
            'previous_year': previous,
            'current_year': current,
            'growth_pct': growth
        })
    return results

def write_output(results, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'ward', 'category', 'previous_year', 'current_year', 'growth_pct'
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"Done! {len(results)} rows written → {output_file}")

def main():
    print(f"Reading: {INPUT_FILE}")
    rows = read_budget(INPUT_FILE)
    print(f"Found {len(rows)} rows")
    flag_nulls(rows)
    results = process_budget(rows)
    write_output(results, OUTPUT_FILE)

if __name__ == "__main__":
    main()
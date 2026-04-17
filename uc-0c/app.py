"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def main():
    raise NotImplementedError("Build this using your AI tool + RICE prompt")
    parser = argparse.ArgumentParser(description="UC-0C Number Aggregator")
    parser.add_argument("--input", required=True, help="Path to input CSV file (e.g., ward_budget.csv)")
    parser.add_argument("--output", required=True, help="Path to write aggregated output (e.g., growth_output.csv)")
    parser.add_argument("--groupby", nargs='+', required=True, help="Fields to group by (e.g., ward category)")
    args = parser.parse_args()

    try:
        result = aggregate_numbers(args.input, args.groupby)
    except Exception as e:
        print(f"Error during aggregation: {e}")
        return

    try:
        write_aggregated_output(args.output, result, args.groupby)
        print(f"Aggregated output written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")


def aggregate_numbers(input_path: str, groupby_fields: list) -> list:
    """
    Aggregates numerical values from an input CSV by specified groupings.
    Returns a list of dicts, each representing a group and its aggregated values.
    """
    import csv
    from collections import defaultdict
    results = {}
    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            key = tuple(row.get(f, '').strip() for f in groupby_fields)
            try:
                value = float(row.get('amount', 0) or 0)
            except Exception:
                value = 0
            if key not in results:
                results[key] = {f: k for f, k in zip(groupby_fields, key)}
                results[key]['total_amount'] = 0
                results[key]['count'] = 0
            results[key]['total_amount'] += value
            results[key]['count'] += 1
    return list(results.values())

def write_aggregated_output(output_path: str, data: list, groupby_fields: list):
    import csv
    if not data:
        raise ValueError("No data to write.")
    fieldnames = groupby_fields + ['total_amount', 'count']
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, '') for k in fieldnames})

if __name__ == "__main__":
    main()

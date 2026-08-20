"""
UC-0C — Number That Looks Right
Calculates budget growth per ward per category with null handling and formula transparency.
"""
import argparse
import csv
import os


NULL_ROWS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}


def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"Dataset loaded: {len(rows)} rows")
    print("\n--- NULL ROWS FLAGGED ---")
    null_count = 0
    for row in rows:
        if not row["actual_spend"]:
            null_count += 1
            print(f"  NULL: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes'] or 'not specified'}")
    print(f"Total nulls: {null_count}\n")
    return rows


def compute_growth(rows, ward, category, growth_type):
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        is_null = not row["actual_spend"]

        if is_null:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL — not computed",
                "formula": "N/A — null value flagged",
                "note": row["notes"] or "no reason given"
            })
            continue

        current = float(row["actual_spend"])

        if growth_type == "MoM":
            if i == 0:
                growth = "N/A — first period"
                formula = "N/A — no previous period"
            else:
                prev_row = filtered[i - 1]
                if not prev_row["actual_spend"]:
                    growth = "NULL — previous period is null"
                    formula = "Cannot compute — previous value is null"
                else:
                    prev = float(prev_row["actual_spend"])
                    pct = (current - prev) / prev * 100
                    growth = f"{pct:+.1f}%"
                    formula = f"({current} - {prev}) / {prev} * 100 = {pct:.1f}%"
        elif growth_type == "YoY":
            prev_period = str(int(period[:4]) - 1) + period[4:]
            prev_rows = [r for r in filtered if r["period"] == prev_period]
            if not prev_rows or not prev_rows[0]["actual_spend"]:
                growth = "N/A — no previous year data"
                formula = "N/A"
            else:
                prev = float(prev_rows[0]["actual_spend"])
                pct = (current - prev) / prev * 100
                growth = f"{pct:+.1f}%"
                formula = f"({current} - {prev}) / {prev} * 100 = {pct:.1f}%"

        results.append({
            "period": period,
            "actual_spend": current,
            "growth": growth,
            "formula": formula,
            "note": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_dataset(args.input)
    print(f"Computing {args.growth_type} growth for: {args.ward} | {args.category}\n")
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth", "formula", "note"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to: {args.output}")
    print("\n--- RESULTS PREVIEW ---")
    print(f"{'Period':<12} {'Spend':>10} {'Growth':>15}  Formula")
    print("-" * 70)
    for r in results:
        print(f"{r['period']:<12} {str(r['actual_spend']):>10} {str(r['growth']):>15}  {r['formula']}")


if __name__ == "__main__":
    main()

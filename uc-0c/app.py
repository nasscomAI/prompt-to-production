"""
UC-0C — Number That Looks Right
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        rows = []
        null_report = []
        for row in reader:
            parsed = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": row["budgeted_amount"].strip(),
                "actual_spend": row["actual_spend"].strip(),
                "notes": row["notes"].strip(),
            }
            if not parsed["actual_spend"]:
                parsed["actual_spend"] = None
                null_report.append({
                    "period": parsed["period"],
                    "ward": parsed["ward"],
                    "category": parsed["category"],
                    "notes": parsed["notes"],
                })
            else:
                try:
                    parsed["actual_spend"] = float(parsed["actual_spend"])
                except ValueError:
                    parsed["actual_spend"] = None
                    null_report.append({
                        "period": parsed["period"],
                        "ward": parsed["ward"],
                        "category": parsed["category"],
                        "notes": f"Invalid value: {parsed['actual_spend']}",
                    })
            rows.append(parsed)

    return rows, null_report


def compute_growth(rows: list, growth_type: str):
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth_type: {growth_type}. Only 'MoM' is supported.")

    sorted_rows = sorted(rows, key=lambda r: r["period"])
    results = []
    prev_spend = None

    for row in sorted_rows:
        period = row["period"]
        spend = row["actual_spend"]
        notes = row["notes"]

        if spend is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_month_spend": "N/A",
                "growth_absolute": "N/A",
                "growth_percent": "N/A",
                "formula_used": "N/A — NULL actual_spend",
                "notes": f"FLAGGED: {notes}" if notes else "FLAGGED: No data",
            })
            prev_spend = None
            continue

        if prev_spend is None:
            results.append({
                "period": period,
                "actual_spend": f"{spend:.1f}",
                "previous_month_spend": "N/A",
                "growth_absolute": "N/A",
                "growth_percent": "N/A",
                "formula_used": "N/A — first period or previous was NULL",
                "notes": notes,
            })
        else:
            growth_abs = spend - prev_spend
            growth_pct = (growth_abs / prev_spend) * 100
            sign = "+" if growth_pct >= 0 else ""
            results.append({
                "period": period,
                "actual_spend": f"{spend:.1f}",
                "previous_month_spend": f"{prev_spend:.1f}",
                "growth_absolute": f"{growth_abs:.1f}",
                "growth_percent": f"{sign}{growth_pct:.1f}%",
                "formula_used": f"({spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f} * 100",
                "notes": notes,
            })

        prev_spend = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category to filter (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM"], help="Growth type: MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)

    print(f"Dataset loaded: {len(rows)} total rows, {len(null_report)} null actual_spend rows")
    if null_report:
        print("Null rows detected:")
        for nr in null_report:
            print(f"  - {nr['period']} | {nr['ward']} | {nr['category']} | {nr['notes']}")

    filtered = [r for r in rows if r["ward"] == args.ward and r["category"] == args.category]
    if not filtered:
        print(f"No rows found for ward='{args.ward}' category='{args.category}'", file=sys.stderr)
        sys.exit(1)

    print(f"Filtered to {len(filtered)} rows for {args.ward} / {args.category}")

    results = compute_growth(filtered, args.growth_type)

    fieldnames = ["period", "actual_spend", "previous_month_spend", "growth_absolute", "growth_percent", "formula_used", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

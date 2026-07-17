"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv


def load_dataset(file_path: str) -> dict:
    """Read CSV, validate columns, report null count and which rows."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except (FileNotFoundError, IOError):
        raise ValueError(f"Error: File not found: {file_path}")

    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required:
        if col not in rows[0]:
            raise ValueError(f"Error: Missing required column: {col}")

    null_rows = []
    for row in rows:
        if not row["actual_spend"].strip():
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided")
            })

    print(f"Loaded {len(rows)} rows. Found {len(null_rows)} null rows.")
    for nr in null_rows:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    return {"data": rows, "null_rows": null_rows}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """Compute growth for a specific ward and category."""
    data = dataset["data"]

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda x: x["period"])

    if not filtered:
        print(f"Error: Ward '{ward}' or category '{category}' not found")
        return []

    results = []
    prev_spend = None

    for row in filtered:
        period = row["period"]
        spend_str = row["actual_spend"].strip()
        notes = row.get("notes", "")

        if not spend_str:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "N/A",
                "formula": "N/A",
                "flag": f"NULL ROW — {notes}"
            })
            prev_spend = None
            continue

        spend = float(spend_str)

        if prev_spend is not None and prev_spend != 0:
            growth = ((spend - prev_spend) / prev_spend) * 100
            formula = f"({spend} - {prev_spend}) / {prev_spend} * 100"
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula,
                "flag": ""
            })
        else:
            results.append({
                "period": period,
                "actual_spend": spend,
                "growth_pct": "N/A (first period)",
                "formula": "N/A",
                "flag": "First period — no previous data"
            })

        prev_spend = spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not results:
        print("No results to write.")
        return

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "actual_spend", "growth_pct", "formula", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

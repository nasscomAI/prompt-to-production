"""
UC-0C — Number That Looks Right
Per-ward per-category growth calculator with null flagging and formula transparency.
"""
import argparse
import csv


def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("Input CSV is empty.")

    missing = required_columns - set(rows[0].keys())
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Report nulls before returning
    null_rows = [r for r in rows if not r["actual_spend"].strip()]
    if null_rows:
        print(f"\nNULL REPORT — {len(null_rows)} rows with missing actual_spend:")
        for r in null_rows:
            print(f"  {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'].strip() or 'no note'}")
    print()

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses to aggregate across wards or categories.
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be MoM or YoY. Refusing to guess.")

    # Filter to exact ward + category only — no cross-ward aggregation
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(f"No data found for ward='{ward}' category='{category}'.")

    # Sort by period
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        spend_raw = row["actual_spend"].strip()

        if not spend_raw:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NOT COMPUTED — NULL",
                "formula": "N/A",
                "flag": f"NULL: {row['notes'].strip() or 'no note'}"
            })
            continue

        spend = float(spend_raw)

        if growth_type == "MoM":
            if i == 0:
                growth_str = "N/A (first period)"
                formula = "N/A"
            else:
                prev_row = filtered[i - 1]
                prev_raw = prev_row["actual_spend"].strip()
                if not prev_raw:
                    growth_str = "NOT COMPUTED — previous period is NULL"
                    formula = "N/A"
                else:
                    prev = float(prev_raw)
                    if prev == 0:
                        growth_str = "NOT COMPUTED — division by zero"
                        formula = "N/A"
                    else:
                        pct = ((spend - prev) / prev) * 100
                        sign = "+" if pct >= 0 else ""
                        growth_str = f"{sign}{pct:.1f}%"
                        formula = f"(({spend} - {prev}) / {prev}) * 100"

        elif growth_type == "YoY":
            growth_str = "N/A (single year dataset)"
            formula = "N/A — only 2024 data available"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": spend,
            "growth": growth_str,
            "formula": formula,
            "flag": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="MoM = Month-on-Month, YoY = Year-on-Year")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Output written to {args.output}")
    print(f"Rows: {len(results)} | Ward: {args.ward} | Category: {args.category} | Growth: {args.growth_type}")


if __name__ == "__main__":
    main()
"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv


def load_dataset(file_path: str) -> dict:
    """Read budget CSV, validate columns, report nulls."""
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if rows:
        actual_cols = set(rows[0].keys())
        missing = expected_cols - actual_cols
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    null_rows = []
    for i, row in enumerate(rows):
        if not row.get("actual_spend", "").strip():
            null_rows.append({
                "row_index": i + 2,
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "notes": row.get("notes", "No reason provided")
            })

    return {
        "data": rows,
        "null_rows": null_rows,
        "null_count": len(null_rows),
        "columns": list(rows[0].keys()) if rows else []
    }


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Compute MoM or YoY growth for specific ward+category."""
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'")

    filtered.sort(key=lambda x: x["period"])

    results = []
    for i, row in enumerate(filtered):
        actual = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        if not actual:
            results.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": "N/A — actual_spend is null",
                "flag": f"NULL: {notes}"
            })
            continue

        actual_val = float(actual)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": "N/A — first period, no previous month",
                    "flag": ""
                })
            else:
                prev_actual = filtered[i - 1].get("actual_spend", "").strip()
                if not prev_actual:
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": f"{actual_val:.1f}",
                        "growth_pct": "NULL",
                        "formula": "N/A — previous month actual_spend is null",
                        "flag": "NULL: cannot compute — previous month has no data"
                    })
                else:
                    prev_val = float(prev_actual)
                    growth = ((actual_val - prev_val) / prev_val) * 100
                    sign = "+" if growth >= 0 else ""
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": f"{actual_val:.1f}",
                        "growth_pct": f"{sign}{growth:.1f}%",
                        "formula": f"({actual_val} - {prev_val}) / {prev_val} * 100",
                        "flag": ""
                    })
        elif growth_type == "YoY":
            prev_period = f"{int(row['period'][:4]) - 1}-{row['period'][5:]}"
            prev_row = next((r for r in filtered if r["period"] == prev_period), None)
            if not prev_row:
                results.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual_val:.1f}",
                    "growth_pct": "N/A",
                    "formula": "N/A — no prior year data",
                    "flag": ""
                })
            else:
                prev_actual = prev_row.get("actual_spend", "").strip()
                if not prev_actual:
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": f"{actual_val:.1f}",
                        "growth_pct": "NULL",
                        "formula": "N/A — prior year actual_spend is null",
                        "flag": "NULL: cannot compute — prior year has no data"
                    })
                else:
                    prev_val = float(prev_actual)
                    growth = ((actual_val - prev_val) / prev_val) * 100
                    sign = "+" if growth >= 0 else ""
                    results.append({
                        "period": row["period"],
                        "ward": ward,
                        "category": category,
                        "actual_spend": f"{actual_val:.1f}",
                        "growth_pct": f"{sign}{growth:.1f}%",
                        "formula": f"({actual_val} - {prev_val}) / {prev_val} * 100",
                        "flag": ""
                    })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    print(f"Loaded {len(dataset['data'])} rows. Found {dataset['null_count']} null actual_spend values.")
    if dataset["null_rows"]:
        for nr in dataset["null_rows"]:
            print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} — {nr['notes']}")

    results = compute_growth(dataset["data"], args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()

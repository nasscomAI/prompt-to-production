"""
UC-0C — Number That Looks Right
Computes per-ward per-category MoM growth with null flagging.
Built using RICE + agents.md + skills.md workflow.
"""
import argparse
import csv
from pathlib import Path


def load_dataset(path: str) -> dict:
    """Read CSV, validate columns, report null count and which rows."""
    filepath = Path(path)
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    rows = []
    nulls = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for i, row in enumerate(reader, start=2):
            rows.append(row)
            if row["actual_spend"].strip() == "":
                nulls.append({
                    "row": i,
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"].strip() if row["notes"].strip() else "No reason provided",
                })

    wards = sorted(set(r["ward"] for r in rows))
    categories = sorted(set(r["category"] for r in rows))

    return {
        "data": rows,
        "nulls": nulls,
        "summary": {
            "total_rows": len(rows),
            "null_count": len(nulls),
            "wards": wards,
            "categories": categories,
        },
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """Compute per-period growth for a specific ward + category."""
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    filtered = [
        r for r in dataset["data"]
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise KeyError(f"No data found for ward='{ward}', category='{category}'")
    if len(filtered) < 2:
        raise ValueError(f"Insufficient data ({len(filtered)} periods) for growth computation")

    filtered.sort(key=lambda r: r["period"])

    period_index = {r["period"]: i for i, r in enumerate(filtered)}

    results = []
    for r in filtered:
        spend_str = r["actual_spend"].strip()
        is_null = spend_str == ""

        null_reason = ""
        if is_null:
            null_reason = r["notes"].strip() if r["notes"].strip() else "No reason provided"

        if is_null:
            results.append({
                "period": r["period"],
                "actual_spend": "NULL",
                "prev_spend": "N/A",
                "growth_pct": "FLAGGED — null actual_spend",
                "formula": "N/A — row flagged",
                "is_null": True,
                "null_reason": null_reason,
            })
            continue

        spend = float(spend_str)
        idx = period_index[r["period"]]

        if growth_type == "MoM":
            if idx == 0:
                results.append({
                    "period": r["period"],
                    "actual_spend": round(spend, 1),
                    "prev_spend": "N/A (first period)",
                    "growth_pct": "N/A (first period)",
                    "formula": "N/A (first period)",
                    "is_null": False,
                    "null_reason": "",
                })
                continue
            prev = filtered[idx - 1]
            prev_spend_str = prev["actual_spend"].strip()
            if prev_spend_str == "":
                results.append({
                    "period": r["period"],
                    "actual_spend": round(spend, 1),
                    "prev_spend": "NULL (previous period)",
                    "growth_pct": "Cannot compute — previous period is NULL",
                    "formula": f"({spend} - NULL) / NULL",
                    "is_null": False,
                    "null_reason": "",
                })
                continue
            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                growth = "Inf (division by zero)"
                formula = f"({spend} - 0) / 0"
            else:
                growth = round(((spend - prev_spend) / prev_spend) * 100, 1)
                sign = "+" if growth >= 0 else ""
                growth = f"{sign}{growth}%"
                formula = f"({spend} - {round(prev_spend, 1)}) / {round(prev_spend, 1)} * 100"

            results.append({
                "period": r["period"],
                "actual_spend": round(spend, 1),
                "prev_spend": round(prev_spend, 1),
                "growth_pct": growth,
                "formula": formula,
                "is_null": False,
                "null_reason": "",
            })

        elif growth_type == "YoY":
            prev_year = str(int(r["period"][:4]) - 1) + r["period"][4:]
            prev_row = next((x for x in filtered if x["period"] == prev_year), None)
            if prev_row is None:
                results.append({
                    "period": r["period"],
                    "actual_spend": round(spend, 1),
                    "prev_spend": "N/A (no prior year)",
                    "growth_pct": "N/A (no prior year)",
                    "formula": "N/A (no prior year)",
                    "is_null": False,
                    "null_reason": "",
                })
                continue
            prev_spend_str = prev_row["actual_spend"].strip()
            if prev_spend_str == "":
                results.append({
                    "period": r["period"],
                    "actual_spend": round(spend, 1),
                    "prev_spend": "NULL (prior year)",
                    "growth_pct": "Cannot compute — prior year is NULL",
                    "formula": f"({spend} - NULL) / NULL",
                    "is_null": False,
                    "null_reason": "",
                })
                continue
            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                growth = "Inf (division by zero)"
                formula = f"({spend} - 0) / 0"
            else:
                growth = round(((spend - prev_spend) / prev_spend) * 100, 1)
                sign = "+" if growth >= 0 else ""
                growth = f"{sign}{growth}%"
                formula = f"({spend} - {round(prev_spend, 1)}) / {round(prev_spend, 1)} * 100"

            results.append({
                "period": r["period"],
                "actual_spend": round(spend, 1),
                "prev_spend": round(prev_spend, 1),
                "growth_pct": growth,
                "formula": formula,
                "is_null": False,
                "null_reason": "",
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    print(f"Loaded {dataset['summary']['total_rows']} rows, {dataset['summary']['null_count']} nulls found:")
    for n in dataset["nulls"]:
        print(f"  Row {n['row']}: {n['period']} | {n['ward']} | {n['category']} | {n['reason']}")

    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["period", "actual_spend", "prev_spend", "growth_pct", "formula", "is_null", "null_reason"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDone. Results written to {args.output}")
    print(f"Computed {len(results)} rows for {args.ward} / {args.category} ({args.growth_type})")


if __name__ == "__main__":
    main()

"""
UC-0C — Number That Looks Right
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
from datetime import datetime
from collections import defaultdict


def load_dataset(file_path: str) -> dict:
    """
    Read ward budget CSV, validate columns, report null count and which rows.
    Returns: dict with keys: rows, null_rows, wards, categories
    """
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or has no headers")

            missing_cols = required_columns - set(reader.fieldnames)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            rows = []
            null_rows = []
            wards = set()
            categories = set()

            for row in reader:
                rows.append(row)
                wards.add(row["ward"])
                categories.add(row["category"])

                actual_spend = row["actual_spend"].strip()
                if not actual_spend:
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row["notes"]
                    })

    except FileNotFoundError:
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading budget file: {e}")

    if not rows:
        raise ValueError("No data rows found in CSV")

    if null_rows:
        print(f"WARNING: Found {len(null_rows)} rows with null actual_spend:")
        for nr in null_rows:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | {nr['notes']}")

    return {
        "rows": rows,
        "null_rows": null_rows,
        "wards": wards,
        "categories": categories
    }


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filter data by ward + category, compute growth per period with formula shown, flag nulls.
    Returns: list of dicts with period, actual_spend, growth_pct, formula, null_flag, null_reason
    """
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("Growth type must be specified (MoM or YoY). Cannot guess.")

    # Filter for ward and category
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"Ward/category combination not found in dataset: {ward} / {category}")

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []

    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if not actual_spend_str:
            results.append({
                "period": period,
                "actual_spend": "",
                "growth_pct": "",
                "formula": "",
                "null_flag": "NULL",
                "null_reason": notes
            })
            continue

        actual_spend = float(actual_spend_str)
        null_flag = ""
        null_reason = ""

        if growth_type == "MoM":
            if i == 0:
                growth_pct = "N/A"
                formula = "No previous period"
            else:
                prev_row = filtered[i - 1]
                prev_spend_str = prev_row["actual_spend"].strip()
                if not prev_spend_str:
                    growth_pct = "N/A"
                    formula = f"Previous period ({prev_row['period']}) has null actual_spend"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_pct = "N/A"
                        formula = f"Previous period actual_spend is 0"
                    else:
                        pct = ((actual_spend - prev_spend) / prev_spend) * 100
                        growth_pct = f"{pct:+.1f}%"
                        formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100 = {pct:+.1f}%"
        else:  # YoY
            # Find same month previous year
            current_year = int(period[:4])
            current_month = period[5:]
            target_period = f"{current_year - 1}-{current_month}"

            prev_row = next((r for r in filtered if r["period"] == target_period), None)
            if not prev_row:
                growth_pct = "N/A"
                formula = f"No data for same month previous year ({target_period})"
            else:
                prev_spend_str = prev_row["actual_spend"].strip()
                if not prev_spend_str:
                    growth_pct = "N/A"
                    formula = f"Previous year period ({target_period}) has null actual_spend"
                else:
                    prev_spend = float(prev_spend_str)
                    if prev_spend == 0:
                        growth_pct = "N/A"
                        formula = f"Previous year actual_spend is 0"
                    else:
                        pct = ((actual_spend - prev_spend) / prev_spend) * 100
                        growth_pct = f"{pct:+.1f}%"
                        formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100 = {pct:+.1f}%"

        results.append({
            "period": period,
            "actual_spend": actual_spend,
            "growth_pct": growth_pct,
            "formula": formula,
            "null_flag": null_flag,
            "null_reason": null_reason
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        data = load_dataset(args.input)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Validate ward and category exist
    if args.ward not in data["wards"]:
        print(f"Error: Ward not found in dataset: {args.ward}")
        print(f"Available wards: {', '.join(sorted(data['wards']))}")
        return

    if args.category not in data["categories"]:
        print(f"Error: Category not found in dataset: {args.category}")
        print(f"Available categories: {', '.join(sorted(data['categories']))}")
        return

    try:
        results = compute_growth(data["rows"], args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Error computing growth: {e}")
        return

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["period", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Growth computation complete. Results written to {args.output}")
        print(f"Ward: {args.ward} | Category: {args.category} | Growth type: {args.growth_type}")
        print(f"Periods processed: {len(results)}")

    except Exception as e:
        print(f"Error writing output file: {e}")
        return


if __name__ == "__main__":
    main()
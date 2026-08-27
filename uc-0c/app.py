"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth (MoM/YoY) from budget CSV data.
"""
import argparse
import csv
import sys


def load_dataset(path: str) -> list:
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("File is empty or has no columns.")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing columns: {', '.join(sorted(missing))}")
        rows = []
        null_rows = []
        for row in reader:
            actual = row["actual_spend"].strip()
            row["budgeted_amount"] = float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else None
            row["actual_spend"] = float(actual) if actual else None
            row["null_flag"] = actual == ""
            row["null_reason"] = row["notes"].strip() if actual == "" else ""
            rows.append(row)
            if row["null_flag"]:
                null_rows.append((row["period"], row["ward"], row["category"], row["null_reason"]))

        print(f"Loaded {len(rows)} rows.", file=sys.stderr)
        if null_rows:
            print(f"Null actual_spend found in {len(null_rows)} rows:", file=sys.stderr)
            for p, w, c, r in null_rows:
                print(f"  {p} | {w} | {c} | {r}", file=sys.stderr)
        else:
            print("No null actual_spend values found.", file=sys.stderr)
        return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        print(f"Warning: No data found for ward '{ward}' / category '{category}'.", file=sys.stderr)
        return []

    results = []

    if growth_type == "MoM":
        formula = "((current - previous) / previous) * 100"
        prev = None
        for r in filtered:
            entry = {
                "period": r["period"],
                "actual_spend": r["actual_spend"],
                "growth_pct": "",
                "formula": formula,
                "null_flag": "TRUE" if r["null_flag"] else "",
                "null_reason": r["null_reason"],
            }
            if r["null_flag"]:
                entry["growth_pct"] = "N/A (null actual_spend)"
            elif prev is None or prev["null_flag"]:
                entry["growth_pct"] = "N/A (no prior period)"
            else:
                prev_val = prev["actual_spend"]
                if prev_val == 0:
                    entry["growth_pct"] = "N/A (division by zero)"
                else:
                    pct = ((r["actual_spend"] - prev_val) / prev_val) * 100
                    entry["growth_pct"] = f"{pct:+.1f}%"
            results.append(entry)
            prev = r

    else:
        formula = "((current - same_period_last_year) / same_period_last_year) * 100"
        for r in filtered:
            entry = {
                "period": r["period"],
                "actual_spend": r["actual_spend"],
                "growth_pct": "N/A (no prior year data)",
                "formula": formula,
                "null_flag": "TRUE" if r["null_flag"] else "",
                "null_reason": r["null_reason"],
            }
            results.append(entry)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Choose 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    if not results:
        print("No results to write.", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "period", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth results written to {args.output} ({len(results)} periods).", file=sys.stderr)


if __name__ == "__main__":
    main()

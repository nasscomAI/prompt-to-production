"""
UC-0C — Budget Growth Analyser
Computes per-period MoM or YoY actual spend growth for a single ward + category.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> dict:
    """Read CSV, validate columns, report nulls before returning data."""
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - fieldnames
            if missing:
                raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Budget file not found: {file_path}")

    null_rows = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"], "notes": r["notes"]}
        for r in rows
        if not r.get("actual_spend", "").strip()
    ]

    return {"rows": rows, "null_count": len(null_rows), "null_rows": null_rows}


def compute_growth(rows: list, growth_type: str) -> list:
    """Compute MoM or YoY growth per period for a pre-filtered ward+category list."""
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Unknown growth_type '{growth_type}'. Please specify either 'MoM' or 'YoY'."
        )

    if not rows:
        raise ValueError("No rows found for the specified ward and category combination.")

    rows = sorted(rows, key=lambda r: r["period"])
    results = []

    for i, row in enumerate(rows):
        period = row["period"]
        raw_spend = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        if not raw_spend:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth_pct": "NULL_FLAGGED",
                "formula": "N/A",
                "null_flag": "NULL_FLAGGED",
                "null_reason": notes or "No reason provided",
            })
            continue

        current = float(raw_spend)

        if growth_type == "MoM":
            if i == 0:
                growth_pct = "N/A (no prior period)"
                formula = "N/A (first period)"
            else:
                prev_row = rows[i - 1]
                prev_spend = prev_row.get("actual_spend", "").strip()
                if not prev_spend:
                    growth_pct = "N/A (prior period is NULL)"
                    formula = "N/A (prior period is NULL)"
                else:
                    prev = float(prev_spend)
                    pct = (current - prev) / prev * 100
                    sign = "+" if pct >= 0 else ""
                    growth_pct = f"{sign}{pct:.1f}%"
                    formula = f"({current} - {prev}) / {prev} × 100"
        else:  # YoY
            if i < 12:
                growth_pct = "N/A (no prior year)"
                formula = "N/A (first year)"
            else:
                prior_row = rows[i - 12]
                prior_spend = prior_row.get("actual_spend", "").strip()
                if not prior_spend:
                    growth_pct = "N/A (prior year period is NULL)"
                    formula = "N/A (prior year period is NULL)"
                else:
                    prior = float(prior_spend)
                    pct = (current - prior) / prior * 100
                    sign = "+" if pct >= 0 else ""
                    growth_pct = f"{sign}{pct:.1f}%"
                    formula = f"({current} - {prior}) / {prior} × 100"

        results.append({
            "period": period,
            "actual_spend": current,
            "growth_pct": growth_pct,
            "formula": formula,
            "null_flag": "",
            "null_reason": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name to filter")
    parser.add_argument("--category",    required=True,  help="Category to filter")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print(
            "ERROR: --growth-type is required. Please specify 'MoM' (month-on-month) "
            "or 'YoY' (year-on-year). Refusing to guess.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)

    if dataset["null_count"] > 0:
        print(f"\nWARNING: {dataset['null_count']} null actual_spend row(s) detected in full dataset:")
        for nr in dataset["null_rows"]:
            print(f"  {nr['period']} · {nr['ward']} · {nr['category']} — {nr['notes']}")
        print()

    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    if not filtered:
        print(
            f"ERROR: No rows found for ward='{args.ward}' category='{args.category}'. "
            "Check spelling matches the CSV exactly.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Computing {args.growth_type} growth for: {args.ward} / {args.category}")

    try:
        results = compute_growth(filtered, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({
                "period": row["period"],
                "ward": args.ward,
                "category": args.category,
                "actual_spend": row["actual_spend"],
                "growth_pct": row["growth_pct"],
                "formula": row["formula"],
                "null_flag": row["null_flag"],
                "null_reason": row["null_reason"],
            })

    print(f"\nResults written to {args.output} ({len(results)} rows)")

    null_in_scope = [r for r in results if r["null_flag"] == "NULL_FLAGGED"]
    if null_in_scope:
        print(f"Flagged {len(null_in_scope)} NULL row(s) within scope:")
        for r in null_in_scope:
            print(f"  {r['period']} — {r['null_reason']}")


if __name__ == "__main__":
    main()

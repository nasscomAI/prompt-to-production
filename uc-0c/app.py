"""
UC-0C — Period-over-period growth calculator for ward budget data.

Implements the agent specification from agents.md and the two skills from
skills.md (load_dataset, compute_growth).
"""
import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    """Read CSV, validate columns, report null actual_spend rows.

    Returns (rows, null_report) where null_report is a list of
    (period, ward, category, notes) for each null row.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row.")

        header = {h.strip() for h in reader.fieldnames}
        missing = REQUIRED_COLUMNS - header
        if missing:
            raise ValueError(
                f"CSV missing required columns: {', '.join(sorted(missing))}"
            )

        rows = []
        null_report = []
        for row in reader:
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            rows.append(cleaned)
            if cleaned["actual_spend"] == "":
                null_report.append((
                    cleaned["period"],
                    cleaned["ward"],
                    cleaned["category"],
                    cleaned["notes"],
                ))

    if null_report:
        print(f"[load_dataset] Warning: {len(null_report)} null actual_spend row(s) found:")
        for period, ward, cat, note in null_report:
            print(f"  {period} | {ward} | {cat} — {note}")

    return rows, null_report


def compute_growth(rows, growth_type):
    """Compute per-period growth for a filtered dataset.

    Returns a list of dicts: period, ward, category, budgeted_amount,
    actual_spend, growth_value, formula.
    """
    valid_types = {"MoM", "YoY"}
    if growth_type not in valid_types:
        raise ValueError(
            f"Unknown growth type '{growth_type}'. Must be one of: {', '.join(sorted(valid_types))}."
        )

    sorted_rows = sorted(rows, key=lambda r: r["period"])

    if len(sorted_rows) < 2:
        raise ValueError(
            f"Need at least 2 periods for {growth_type} growth, got {len(sorted_rows)}."
        )

    results = []
    last_valid_spend = None

    for row in sorted_rows:
        period = row["period"]
        ward = row["ward"]
        category = row["category"]
        budgeted = float(row["budgeted_amount"])
        is_null = row["actual_spend"] == ""
        notes = row["notes"]

        entry = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": "" if is_null else float(row["actual_spend"]),
            "growth_value": "",
            "formula": "",
        }

        if is_null:
            entry["growth_value"] = f"NULL — {notes}"
            entry["formula"] = "Not computed (null actual_spend)"
            results.append(entry)
            continue

        current = float(row["actual_spend"])

        if last_valid_spend is None:
            entry["growth_value"] = "N/A (first period)"
            if growth_type == "MoM":
                entry["formula"] = "No previous month for MoM comparison"
            else:
                entry["formula"] = "No previous year for YoY comparison"
        else:
            growth = ((current - last_valid_spend) / last_valid_spend) * 100
            entry["growth_value"] = f"{growth:+.1f}%"
            if growth_type == "MoM":
                entry["formula"] = "MoM = (current − previous) / previous × 100"
            else:
                entry["formula"] = "YoY = (current − previous) / previous × 100"

        last_valid_spend = current
        results.append(entry)

    return results


def write_output(filepath, results):
    """Write growth results to a CSV file."""
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)

    fieldnames = [
        "period", "ward", "category", "budgeted_amount",
        "actual_spend", "growth_value", "formula",
    ]
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nOutput written to {filepath}")


def get_pairs(rows):
    """Return sorted list of unique (ward, category) pairs."""
    pairs = sorted({(r["ward"], r["category"]) for r in rows})
    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Period-over-period growth calculator"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="ALL", help="Ward to filter (default: ALL). Use 'ALL' for all wards.")
    parser.add_argument("--category", default="ALL", help="Category to filter (default: ALL). Use 'ALL' for all categories.")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    pairs = get_pairs(rows)

    if args.ward == "ALL" and args.category == "ALL":
        combos = pairs
    elif args.ward == "ALL":
        combos = [(w, c) for (w, c) in pairs if c == args.category]
    elif args.category == "ALL":
        combos = [(w, c) for (w, c) in pairs if w == args.ward]
    else:
        combos = [(args.ward, args.category)]

    if not combos:
        print(f"No data found for ward '{args.ward}' and category '{args.category}'.")
        sys.exit(1)

    all_results = []
    for ward, category in combos:
        filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
        results = compute_growth(filtered, args.growth_type)
        all_results.extend(results)

    write_output(args.output, all_results)


if __name__ == "__main__":
    main()

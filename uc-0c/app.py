"""
UC-0C app.py — Growth calculator for municipal budget data.

Implements the load_dataset and compute_growth skills described in skills.md,
bounded by the enforcement rules in agents.md:
  - Never aggregate across wards or categories
  - Flag every null row before computing — report null reason from notes
  - Show formula used in every output row alongside the result
  - Refuse if --growth-type is not specified
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = {"MoM": "monthly"}


def load_dataset(input_path):
    """Read CSV, validate columns, and report null rows before returning."""
    if not os.path.isfile(input_path):
        raise ValueError(
            f"Input file not found: {input_path}. Refusing rather than guessing."
        )

    with open(input_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("Input file is empty or missing a header row.")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"Input file is missing required columns: {missing}. "
                "Refusing to proceed with unvalidated data."
            )
        rows = list(reader)

    null_rows = []
    for row in rows:
        if not row["actual_spend"].strip():
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"].strip() or "No reason given",
                }
            )

    print(f"Validated {len(rows)} rows from {input_path}.")
    print(f"Null actual_spend rows: {len(null_rows)}")
    for n in null_rows:
        print(
            f"  FLAGGED — {n['period']} · {n['ward']} · "
            f"{n['category']} · reason: {n['reason']}"
        )
    if null_rows:
        print("  These rows are flagged, never computed, never silently skipped.")

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type, null_rows):
    """Per-period growth for one ward + category with formula shown per row."""
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. Supported: "
            f"{', '.join(sorted(SUPPORTED_GROWTH_TYPES))}. Refusing rather than guessing."
        )

    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError(
            f"No rows found for ward '{ward}' and category '{category}'. "
            "Refusing rather than inventing numbers."
        )

    filtered.sort(key=lambda r: r["period"])
    null_by_key = {
        (n["ward"], n["category"], n["period"]): n for n in null_rows
    }

    if growth_type == "MoM":
        formula = "MoM = (actual_spend[t] - actual_spend[t-1]) / actual_spend[t-1] * 100"
        output = []
        for idx, row in enumerate(filtered):
            period = row["period"]
            null = null_by_key.get((ward, category, period))
            if null is not None:
                output.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": "",
                        "growth_pct": "FLAGGED",
                        "formula": formula,
                        "note": null["reason"],
                    }
                )
                continue
            actual = float(row["actual_spend"])
            prev_key = (ward, category, filtered[idx - 1]["period"]) if idx > 0 else None
            if idx > 0 and prev_key not in null_by_key:
                prev = float(filtered[idx - 1]["actual_spend"])
                if prev == 0:
                    growth = "n/a"
                else:
                    growth = round((actual - prev) / prev * 100, 1)
            else:
                growth = "n/a"
            output.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "growth_pct": growth,
                    "formula": formula,
                    "note": "",
                }
            )
        return output

    raise ValueError(f"Unhandled growth type: {growth_type}")


def write_output(output_path, rows):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "note"]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_path}.")


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C growth calculator for one ward + category."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g. 'MoM'. Required — never guessed.")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)
        result = compute_growth(
            rows, args.ward, args.category, args.growth_type, null_rows
        )
        write_output(args.output, result)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

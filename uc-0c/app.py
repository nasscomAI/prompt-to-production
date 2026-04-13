"""
UC-0C — Budget Growth Calculator
Implements load_dataset and compute_growth per agents.md and skills.md.
"""
import argparse
import csv
import os

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


# ---------------------------------------------------------------------------
# skill: load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str):
    """
    Read the ward budget CSV, validate required columns, and report null
    actual_spend rows before returning.

    Input:  path to budget CSV (str)
    Output: tuple of (list-of-row-dicts, list-of-null-row-dicts)
            null rows each contain: period, ward, category, notes
    Error handling (skills.md):
      - FileNotFoundError if file missing
      - ValueError if a required column is absent or file has no data rows
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"No data found in file: {file_path}")

        actual_fields = {c.strip() for c in reader.fieldnames}
        missing = REQUIRED_COLUMNS - actual_fields
        if missing:
            raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

        rows = [row for row in reader]

    if not rows:
        raise ValueError(f"No data rows found in file: {file_path}")

    null_rows = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_rows.append({
                "period":   row["period"].strip(),
                "ward":     row["ward"].strip(),
                "category": row["category"].strip(),
                "notes":    row.get("notes", "").strip(),
            })

    return rows, null_rows


# ---------------------------------------------------------------------------
# skill: compute_growth
# ---------------------------------------------------------------------------

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for a specific ward + category.

    Input:  rows (list of dicts from load_dataset), ward (str),
            category (str), growth_type (str — "MoM" or "YoY")
    Output: list of dicts with: period, actual_spend, formula, growth_pct, flagged
    Error handling (agents.md + skills.md):
      - ValueError if growth_type is not "MoM" or "YoY"
      - ValueError if no rows match the given ward + category
      - ValueError if result spans multiple ward-category combinations
    """
    # agents.md enforcement rule 4: refuse unknown growth_type — never default
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"growth_type must be 'MoM' or 'YoY' — got '{growth_type}'. "
            "Please specify one explicitly."
        )

    # Filter to the requested ward + category — agents.md enforcement rule 1
    filtered = [
        r for r in rows
        if r["ward"].strip() == ward and r["category"].strip() == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}', category='{category}'."
        )

    # Guard: never silently aggregate if filter returns mixed combinations
    combos = {(r["ward"].strip(), r["category"].strip()) for r in filtered}
    if len(combos) > 1:
        raise ValueError(
            "Result spans multiple ward-category combinations — "
            "specify a single ward and category."
        )

    # Sort by period
    filtered.sort(key=lambda r: r["period"].strip())

    # Build a parallel list of (period, spend_or_none) for growth calculation
    periods = []
    for r in filtered:
        raw = r.get("actual_spend", "").strip()
        spend = float(raw) if raw != "" else None
        periods.append((r["period"].strip(), spend, r.get("notes", "").strip()))

    result = []
    for i, (period, spend, notes) in enumerate(periods):
        # agents.md enforcement rule 2: flag nulls, do not compute
        if spend is None:
            result.append({
                "period":       period,
                "actual_spend": "",
                "formula":      f"NULL — not computed (reason: {notes or 'no notes'})",
                "growth_pct":   None,
                "flagged":      True,
            })
            continue

        # Find the comparison period
        prev_spend = None
        prev_period = None
        if growth_type == "MoM" and i > 0:
            prev_spend = periods[i - 1][1]
            prev_period = periods[i - 1][0]
        elif growth_type == "YoY":
            # Find same month, prior year
            y, m = period[:4], period[5:7]
            prev_year_period = f"{int(y) - 1}-{m}"
            for p, s, _ in periods:
                if p == prev_year_period:
                    prev_spend = s
                    prev_period = prev_year_period
                    break

        if prev_spend is None or prev_period is None:
            # No comparable prior period available
            formula = f"No prior {growth_type} period available"
            result.append({
                "period":       period,
                "actual_spend": spend,
                "formula":      formula,
                "growth_pct":   None,
                "flagged":      False,
            })
        elif prev_spend == 0:
            formula = f"{growth_type}: ({spend} − {prev_spend}) / {prev_spend} = undefined (division by zero)"
            result.append({
                "period":       period,
                "actual_spend": spend,
                "formula":      formula,
                "growth_pct":   None,
                "flagged":      False,
            })
        else:
            # agents.md enforcement rule 3: show formula alongside result
            growth = (spend - prev_spend) / prev_spend * 100
            sign = "+" if growth >= 0 else ""
            formula = (
                f"{growth_type}: ({spend} − {prev_spend}) / {prev_spend} "
                f"= {sign}{growth:.1f}%"
            )
            result.append({
                "period":       period,
                "actual_spend": spend,
                "formula":      formula,
                "growth_pct":   round(growth, 1),
                "flagged":      False,
            })

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Ward name (exact string)")
    parser.add_argument("--category",    required=True,  help="Category name (exact string)")
    parser.add_argument("--growth-type", required=True,  dest="growth_type",
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-on-month) or YoY (year-on-year)")
    parser.add_argument("--output",      required=True,  help="Path to write results CSV")
    args = parser.parse_args()

    # skill: load_dataset — report nulls before computing
    rows, null_rows = load_dataset(args.input)

    if null_rows:
        print(f"\nNULL ROWS DETECTED ({len(null_rows)}) — flagged, not computed:")
        for nr in null_rows:
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | {nr['notes'] or 'no notes'}")
        print()

    # skill: compute_growth
    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    # Write output CSV — agents.md enforcement rule 3: formula in every row
    fieldnames = ["period", "actual_spend", "growth_pct", "formula", "flagged"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

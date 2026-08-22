"""
UC-0C app.py — Number That Looks Right.
Built from the RICE prompt in agents.md.

Deterministic per-ward per-category growth calculator. Refuses all-ward
aggregation, refuses a missing/invalid --growth-type, and reports every
null actual_spend row instead of silently skipping or averaging it — the
exact failure modes (wrong aggregation level, silent null handling,
formula assumption) this UC is testing for. See README.md for run command
and expected behaviour.
"""
import argparse
import csv
import sys


def load_dataset(path: str):
    """
    Read ward_budget.csv, validate columns, report nulls before returning.
    Returns: list of row dicts with actual_spend as float or None.
    """
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input file is missing required columns: {sorted(missing)}")
        rows = list(reader)

    nulls = []
    for row in rows:
        raw = (row.get("actual_spend") or "").strip()
        if raw == "":
            row["actual_spend"] = None
            nulls.append(row)
        else:
            try:
                row["actual_spend"] = float(raw)
            except ValueError:
                row["actual_spend"] = None
                nulls.append(row)

    print(f"load_dataset: {len(rows)} rows loaded, {len(nulls)} null actual_spend rows found:")
    for row in nulls:
        print(f"  - {row['period']} · {row['ward']} · {row['category']} — {row.get('notes', '').strip()}")

    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for exactly one ward+category pair.
    Refuses (raises ValueError) on missing/ambiguous scope or growth_type.
    """
    if not ward or ward.strip().lower() in ("", "all"):
        raise ValueError("Refused: --ward is required and must name one exact ward. All-ward aggregation is not supported.")
    if not category or category.strip().lower() in ("", "all"):
        raise ValueError("Refused: --category is required and must name one exact category. All-category aggregation is not supported.")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("Refused: --growth-type must be exactly 'MoM' or 'YoY'. Not guessing a default.")

    series = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    if not series:
        raise ValueError(f"Refused: no rows found for ward={ward!r} category={category!r}. Check exact spelling against the source CSV.")

    by_period = {r["period"]: r for r in series}
    results = []

    for row in series:
        period = row["period"]
        actual = row["actual_spend"]

        if actual is None:
            results.append({
                "period": period, "actual_spend": "", "growth_pct": "",
                "formula": f"{growth_type} not computed — actual_spend is null.",
                "flag": "NULL_ACTUAL",
            })
            continue

        if growth_type == "MoM":
            year, month = period.split("-")
            prev_month = int(month) - 1
            prev_year = int(year)
            if prev_month == 0:
                prev_month, prev_year = 12, prev_year - 1
            baseline_period = f"{prev_year:04d}-{prev_month:02d}"
        else:  # YoY
            year, month = period.split("-")
            baseline_period = f"{int(year) - 1:04d}-{month}"

        baseline_row = by_period.get(baseline_period)
        if baseline_row is None or baseline_row["actual_spend"] is None:
            reason = "not present in dataset" if baseline_row is None else "is null"
            results.append({
                "period": period, "actual_spend": actual, "growth_pct": "",
                "formula": f"{growth_type} not computed — baseline period {baseline_period} {reason}.",
                "flag": "NULL_COMPARISON",
            })
            continue

        baseline = baseline_row["actual_spend"]
        growth_pct = (actual - baseline) / baseline * 100
        formula = (
            f"{growth_type} = (current - previous) / previous x 100 "
            f"= ({actual} - {baseline}) / {baseline} x 100 = {growth_pct:+.1f}%"
        )
        results.append({
            "period": period, "actual_spend": actual,
            "growth_pct": f"{growth_pct:+.1f}%", "formula": formula, "flag": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows = load_dataset(args.input)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "period": r["period"], "ward": args.ward, "category": args.category,
                "actual_spend": r["actual_spend"], "growth_pct": r["growth_pct"],
                "formula": r["formula"], "flag": r["flag"],
            })

    print(f"Done. {len(results)} periods written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Number That Looks Right
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str):
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows.
    Returns: list of row dicts with actual_spend as float or None.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"ward_budget.csv is missing required columns: {missing}")

        rows = []
        for raw in reader:
            actual_raw = (raw.get("actual_spend") or "").strip()
            rows.append({
                "period": raw["period"].strip(),
                "ward": raw["ward"].strip(),
                "category": raw["category"].strip(),
                "budgeted_amount": float(raw["budgeted_amount"]),
                "actual_spend": float(actual_raw) if actual_raw else None,
                "notes": (raw.get("notes") or "").strip(),
            })

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"Loaded {len(rows)} rows. {len(null_rows)} rows have null actual_spend:")
    for r in null_rows:
        reason = r["notes"] or "no reason given"
        print(f"  - {r['period']} | {r['ward']} | {r['category']} -> {reason}")

    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute a per-period growth table for exactly one ward + one category.
    Returns: list of dicts {period, ward, category, budgeted_amount,
    actual_spend, formula, growth_pct, flag, note}
    """
    series = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    if not series:
        raise ValueError(f"No rows found for ward='{ward}' category='{category}'.")

    by_period = {r["period"]: r for r in series}

    def prior_period_key(period: str):
        year, month = period.split("-")
        year, month = int(year), int(month)
        if growth_type == "MoM":
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)
        else:  # YoY
            year -= 1
        return f"{year:04d}-{month:02d}"

    output = []
    for row in series:
        entry = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"] if row["actual_spend"] is not None else "",
            "formula": "",
            "growth_pct": "",
            "flag": "",
            "note": "",
        }

        if row["actual_spend"] is None:
            entry["flag"] = "NULL_ACTUAL"
            entry["note"] = row["notes"] or "actual_spend not available for this period"
            output.append(entry)
            continue

        prior_key = prior_period_key(row["period"])
        prior_row = by_period.get(prior_key)

        if prior_row is None:
            entry["flag"] = "NO_PRIOR_PERIOD"
            entry["note"] = f"No {prior_key} row exists in this dataset for {growth_type} comparison."
            output.append(entry)
            continue

        if prior_row["actual_spend"] is None:
            entry["flag"] = "PRIOR_PERIOD_UNAVAILABLE"
            entry["note"] = (
                f"Prior period {prior_key} actual_spend is null "
                f"({prior_row['notes'] or 'no reason given'}); growth cannot be computed."
            )
            output.append(entry)
            continue

        cur, prev = row["actual_spend"], prior_row["actual_spend"]
        growth_pct = round((cur - prev) / prev * 100, 1)
        entry["formula"] = f"({cur} - {prev}) / {prev} * 100"
        entry["growth_pct"] = growth_pct
        output.append(entry)

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", default=None, help="Exact category name")
    parser.add_argument("--growth-type", default=None, choices=["MoM", "YoY"],
                         help="MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.ward or not args.category:
        print(
            "REFUSED: this agent never aggregates across wards or categories. "
            "Pass --ward and --category explicitly to compute a single series."
        )
        return

    if not args.growth_type:
        print("REFUSED: --growth-type must be specified explicitly as MoM or YoY. Not guessing.")
        return

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "formula", "growth_pct", "flag", "note"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} periods written to {args.output}")


if __name__ == "__main__":
    main()

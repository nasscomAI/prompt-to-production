"""
UC-0C — Number That Looks Right
Implements load_dataset and compute_growth per agents.md (RICE) and skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> dict:
    """
    Read ward budget CSV, validate columns, report nulls before returning.
    Returns {"rows": [...], "null_rows": [...]}.
    Raises FileNotFoundError or ValueError on bad input.
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])

            # --- skills.md: validate all required columns present ---
            missing_cols = REQUIRED_COLUMNS - fieldnames
            if missing_cols:
                raise ValueError(
                    f"CSV missing required column(s): {', '.join(sorted(missing_cols))}"
                )

            raw_rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    rows = []
    null_rows = []

    for r in raw_rows:
        spend_raw = r["actual_spend"].strip()
        actual_spend = None if spend_raw == "" else float(spend_raw)

        row = {
            "period":          r["period"].strip(),
            "ward":            r["ward"].strip(),
            "category":        r["category"].strip(),
            "budgeted_amount": float(r["budgeted_amount"]),
            "actual_spend":    actual_spend,
            "notes":           r["notes"].strip(),
        }
        rows.append(row)
        if actual_spend is None:
            null_rows.append(row)

    # --- agents.md: enforcement rule 2 — report nulls before any computation ---
    print(f"Dataset loaded: {len(rows)} rows, {len(null_rows)} null actual_spend value(s).")
    if null_rows:
        print("NULL rows (will not be computed):")
        for nr in null_rows:
            reason = nr["notes"] if nr["notes"] else "no reason recorded"
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} — {reason}")

    return {"rows": rows, "null_rows": null_rows}


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for a single ward+category slice.
    Returns list of dicts: period, actual_spend, growth_value, formula_used, null_flag.
    Raises ValueError if growth_type missing, or ward/category slice is empty.
    """
    # --- agents.md: enforcement rule 4 — refuse if growth_type not explicit ---
    if not growth_type or growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "growth_type must be explicitly 'MoM' or 'YoY' — "
            "please specify --growth-type. Never guessed."
        )

    # --- agents.md: enforcement rule 1 — exact slice only, no cross-ward/category ---
    slice_rows = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]

    if not slice_rows:
        raise ValueError(
            f"No rows found for ward='{ward}', category='{category}'. "
            f"Check exact spelling including dashes and special characters."
        )

    # Sort by period ascending
    slice_rows = sorted(slice_rows, key=lambda r: r["period"])

    results = []
    for i, row in enumerate(slice_rows):
        period       = row["period"]
        actual_spend = row["actual_spend"]
        null_flag    = ""
        growth_value = None
        formula_used = ""

        # --- agents.md: enforcement rule 2 — flag nulls, report reason ---
        if actual_spend is None:
            null_flag    = f"NULL: {row['notes'] if row['notes'] else 'no reason recorded'}"
            formula_used = "NOT COMPUTED — actual_spend is null"
        else:
            if growth_type == "MoM":
                # Find previous month's row
                prev = slice_rows[i - 1] if i > 0 else None
                if prev is None:
                    formula_used = "MoM — no prior period available"
                elif prev["actual_spend"] is None:
                    formula_used = f"MoM — prior period {prev['period']} is null; cannot compute"
                    null_flag    = f"PRIOR NULL: {prev['notes'] if prev['notes'] else 'no reason'}"
                else:
                    prev_val = prev["actual_spend"]
                    growth_value = round((actual_spend - prev_val) / prev_val * 100, 1)
                    sign = "+" if growth_value >= 0 else ""
                    # --- agents.md: enforcement rule 3 — formula visible in every row ---
                    formula_used = (
                        f"MoM = ({actual_spend} - {prev_val}) / {prev_val} * 100 "
                        f"= {sign}{growth_value}%"
                    )

            elif growth_type == "YoY":
                # Find same month prior year (period is YYYY-MM)
                year, month = period.split("-")
                prior_period = f"{int(year) - 1}-{month}"
                prior_rows = [r for r in slice_rows if r["period"] == prior_period]
                if not prior_rows:
                    formula_used = f"YoY — no prior-year period {prior_period} available"
                elif prior_rows[0]["actual_spend"] is None:
                    formula_used = f"YoY — prior period {prior_period} is null; cannot compute"
                    null_flag    = f"PRIOR NULL: {prior_rows[0]['notes']}"
                else:
                    prior_val = prior_rows[0]["actual_spend"]
                    growth_value = round((actual_spend - prior_val) / prior_val * 100, 1)
                    sign = "+" if growth_value >= 0 else ""
                    formula_used = (
                        f"YoY = ({actual_spend} - {prior_val}) / {prior_val} * 100 "
                        f"= {sign}{growth_value}%"
                    )

        results.append({
            "period":       period,
            "actual_spend": actual_spend,
            "growth_value": growth_value,
            "formula_used": formula_used,
            "null_flag":    null_flag,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help="Exact ward name")
    parser.add_argument("--category",    required=True,  help="Exact category name")
    parser.add_argument("--growth-type", required=True,  help="MoM or YoY")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(
        dataset["rows"],
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    out_fields = ["period", "actual_spend", "growth_value", "formula_used", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    nulls   = sum(1 for r in results if r["null_flag"])
    computed = sum(1 for r in results if r["growth_value"] is not None)
    print(f"Growth computed: {computed} period(s), {nulls} null/skipped row(s).")
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C app.py — Ward budget growth calculator.

Computes period-over-period growth (MoM or YoY) of actual_spend for a single
ward + category slice. Enforces the rules in agents.md:
  - Never aggregates across wards or categories (refuses if asked).
  - Flags every null actual_spend row with its reason; never treats null as 0.
  - Shows the exact formula used in every output row.
  - Refuses if --growth-type is not specified (never guesses).

See README.md for the run command and expected behaviour.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

# Tokens that indicate an attempt to aggregate across the (ward, category) boundary.
AGGREGATE_TOKENS = {"all", "all wards", "all categories", "total", "overall",
                    "everything", "combined", "sum", "aggregate", "*"}


class RefusalError(Exception):
    """Raised when the request violates an enforcement rule and must be refused."""


def _parse_float(value):
    """Parse a spend/budget cell. Blank -> None (never 0.0)."""
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    return float(text)


def load_dataset(path):
    """
    Read and validate the CSV. Returns (rows, null_report).

    rows: list of dicts with actual_spend/budgeted_amount as float-or-None.
    null_report: list of dicts describing each null actual_spend row.
    """
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            header = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in header]
            if missing:
                raise RefusalError(
                    f"Input CSV is missing required column(s): {', '.join(missing)}. "
                    f"Expected columns: {', '.join(REQUIRED_COLUMNS)}."
                )
            rows = []
            for raw in reader:
                rows.append({
                    "period": (raw["period"] or "").strip(),
                    "ward": (raw["ward"] or "").strip(),
                    "category": (raw["category"] or "").strip(),
                    "budgeted_amount": _parse_float(raw["budgeted_amount"]),
                    "actual_spend": _parse_float(raw["actual_spend"]),
                    "notes": (raw["notes"] or "").strip(),
                })
    except FileNotFoundError:
        raise RefusalError(f"Input file not found: {path}")

    null_report = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"],
         "reason": r["notes"] or "(no reason given in notes)"}
        for r in rows if r["actual_spend"] is None
    ]
    return rows, null_report


def _reject_if_aggregate(name, kind):
    if name is None or name.strip().lower() in AGGREGATE_TOKENS:
        raise RefusalError(
            f"Refusing to aggregate across {kind}s. This tool reports a single "
            f"(ward, category) slice only. Specify one concrete {kind}."
        )


def compute_growth(rows, ward, category, growth_type):
    """
    Compute per-period growth for one ward + category. Returns an ordered list
    of output-row dicts. Null current/comparison values yield flagged, uncomputed rows.
    """
    growth_type = (growth_type or "").strip()
    if growth_type not in ("MoM", "YoY"):
        raise RefusalError(
            "--growth-type is required and must be 'MoM' or 'YoY'. "
            "Refusing to guess which growth calculation you want."
        )

    _reject_if_aggregate(ward, "ward")
    _reject_if_aggregate(category, "category")

    # Validate that the requested slice actually exists.
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})
    if ward not in wards:
        raise RefusalError(
            f"Ward '{ward}' not found. Valid wards: {', '.join(wards)}."
        )
    if category not in categories:
        raise RefusalError(
            f"Category '{category}' not found. Valid categories: {', '.join(categories)}."
        )

    # Slice: only this ward AND this category, ordered by period.
    slice_rows = sorted(
        (r for r in rows if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    spend_by_period = {r["period"]: r for r in slice_rows}

    lag = 1 if growth_type == "MoM" else 12
    results = []
    for idx, r in enumerate(slice_rows):
        period = r["period"]
        current = r["actual_spend"]

        # Identify the comparison period.
        if growth_type == "MoM":
            prior_row = slice_rows[idx - 1] if idx - lag >= 0 else None
        else:  # YoY: same month previous year -> not present in a single 2024 dataset
            prior_period = _shift_year(period, -1)
            prior_row = spend_by_period.get(prior_period)

        prior_period_label = prior_row["period"] if prior_row else "n/a"
        prior = prior_row["actual_spend"] if prior_row else None

        row_out = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": current,
            "growth_type": growth_type,
            "comparison_period": prior_period_label,
            "comparison_value": prior,
            "growth_pct": "",
            "formula": "",
            "flag": "",
        }

        if current is None:
            row_out["flag"] = f"NULL — {r['notes'] or 'no reason given'}"
            row_out["formula"] = "not computed (current actual_spend is null)"
        elif prior_row is None:
            row_out["flag"] = "no comparison period available"
            row_out["formula"] = f"not computed (no {growth_type} baseline in dataset)"
        elif prior is None:
            row_out["flag"] = f"comparison period {prior_period_label} is NULL — {prior_row['notes'] or 'no reason given'}"
            row_out["formula"] = "not computed (comparison actual_spend is null)"
        else:
            growth = (current - prior) / prior * 100.0
            row_out["growth_pct"] = round(growth, 1)
            row_out["formula"] = (
                f"({current} - {prior}) / {prior} * 100 = {round(growth, 1)}%"
            )
        results.append(row_out)

    return results


def _shift_year(period, delta):
    """period is 'YYYY-MM'. Return same month, year+delta."""
    year, month = period.split("-")
    return f"{int(year) + delta:04d}-{month}"


def write_output(results, path):
    fields = ["ward", "category", "period", "actual_spend", "growth_type",
              "comparison_period", "comparison_value", "growth_pct", "formula", "flag"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="Compute per-ward, per-category budget growth (MoM or YoY)."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward")
    parser.add_argument("--category", required=True, help="Exactly one category")
    # Intentionally NOT given a default: absence must trigger a refusal, not a guess.
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY (required — no default)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        rows, null_report = load_dataset(args.input)

        # Report nulls BEFORE computing anything.
        print(f"Loaded {len(rows)} rows from {args.input}.")
        print(f"Null actual_spend rows found: {len(null_report)}")
        for n in null_report:
            print(f"  - {n['period']} · {n['ward']} · {n['category']} → {n['reason']}")
        print()

        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(results, args.output)

        computed = sum(1 for r in results if r["growth_pct"] != "")
        flagged = sum(1 for r in results if r["flag"])
        print(f"Wrote {len(results)} rows for {args.ward} · {args.category} "
              f"({args.growth_type}) to {args.output}.")
        print(f"  {computed} rows with computed growth, {flagged} flagged/uncomputed.")
    except RefusalError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

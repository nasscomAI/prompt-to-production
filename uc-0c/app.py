"""
UC-0C — Number That Looks Right

Per-ward, per-category budget growth calculator built to the enforcement rules
in agents.md and the skill contracts in skills.md.

Run:
    python app.py --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
        --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_FIELDS = ["period", "ward", "category", "actual_spend", "growth_type", "formula", "growth_pct", "flag"]


def _norm(text: str) -> str:
    """Normalise ward/category strings: unify dashes, collapse whitespace, lowercase."""
    if text is None:
        return ""
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return " ".join(text.split()).strip().lower()


# --- Skill: load_dataset ----------------------------------------------------

def load_dataset(input_path: str):
    """
    Read the budget CSV, validate columns, and report null actual_spend rows.

    Returns (rows, null_report).
    """
    try:
        fh = open(input_path, "r", newline="", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: could not open input file '{input_path}': {exc}", file=sys.stderr)
        raise SystemExit(1)

    rows = []
    null_report = []
    with fh:
        reader = csv.DictReader(fh)
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing_cols:
            print(f"ERROR: input is missing required column(s): {missing_cols}", file=sys.stderr)
            raise SystemExit(1)

        for raw in reader:
            spend_raw = (raw.get("actual_spend") or "").strip()
            actual_spend = None if spend_raw == "" else float(spend_raw)
            row = {
                "period": (raw.get("period") or "").strip(),
                "ward": (raw.get("ward") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "budgeted_amount": (raw.get("budgeted_amount") or "").strip(),
                "actual_spend": actual_spend,
                "notes": (raw.get("notes") or "").strip(),
            }
            rows.append(row)
            if actual_spend is None:
                null_report.append({
                    "period": row["period"], "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"] or "(no reason given in notes)",
                })

    return rows, null_report


# --- Skill: compute_growth --------------------------------------------------

def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for ONE ward + ONE category using growth_type.

    Returns (result_rows, error). If error is not None, result_rows is empty and
    error is a human-readable refusal message.
    """
    # Enforcement: refuse aggregation / missing scope.
    if not ward or _norm(ward) in ("", "all", "all wards"):
        return [], "REFUSED: a specific ward is required. This tool never aggregates across wards."
    if not category or _norm(category) in ("", "all", "all categories"):
        return [], "REFUSED: a specific category is required. This tool never aggregates across categories."

    # Enforcement: refuse if growth type not chosen.
    if not growth_type:
        return [], "REFUSED: --growth-type not specified. Please choose MoM or YoY. The tool will not guess."
    gtype = growth_type.strip().upper()
    if gtype not in ("MOM", "YOY"):
        return [], f"REFUSED: unknown growth type '{growth_type}'. Use MoM or YoY."
    gtype = "MoM" if gtype == "MOM" else "YoY"

    # Filter to the single ward + category (dash/case tolerant).
    subset = [
        r for r in rows
        if _norm(r["ward"]) == _norm(ward) and _norm(r["category"]) == _norm(category)
    ]
    if not subset:
        return [], f"REFUSED: no rows found for ward '{ward}' and category '{category}'."

    subset.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in subset}

    def prior_period(period: str) -> str:
        year, month = period.split("-")
        year, month = int(year), int(month)
        if gtype == "MoM":
            month -= 1
            if month == 0:
                month, year = 12, year - 1
        else:  # YoY
            year -= 1
        return f"{year:04d}-{month:02d}"

    results = []
    for r in subset:
        period = r["period"]
        cur = r["actual_spend"]
        prev_key = prior_period(period)
        prev_row = by_period.get(prev_key)
        prev = prev_row["actual_spend"] if prev_row else None

        formula = f"{gtype} = (curr - prev) / prev * 100"
        flag = ""
        growth_pct = "NOT COMPUTED"

        if cur is None:
            growth_pct = "NOT COMPUTED"
            flag = f"NULL actual_spend for {period}: {r['notes'] or 'no reason given'}"
        elif prev_row is None:
            growth_pct = "NOT COMPUTED"
            reason = "no prior-year data" if gtype == "YoY" else "no prior month in data"
            flag = f"No comparison period ({prev_key}): {reason}"
        elif prev is None:
            growth_pct = "NOT COMPUTED"
            flag = f"Comparison period {prev_key} has NULL actual_spend: {prev_row['notes'] or 'no reason given'}"
        elif prev == 0:
            growth_pct = "NOT COMPUTED"
            flag = f"Comparison period {prev_key} spend is 0; growth undefined"
        else:
            growth_pct = round((cur - prev) / prev * 100, 1)
            formula = f"{gtype} = ({cur} - {prev}) / {prev} * 100 = {growth_pct}%"

        results.append({
            "period": period,
            "ward": r["ward"],
            "category": r["category"],
            "actual_spend": "" if cur is None else cur,
            "growth_type": gtype,
            "formula": formula,
            "growth_pct": growth_pct,
            "flag": flag,
        })

    return results, None


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="", help="Exact ward name (required)")
    parser.add_argument("--category", default="", help="Exact category name (required)")
    parser.add_argument("--growth-type", dest="growth_type", default="",
                        help="MoM or YoY (required — never guessed)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)

    # Enforcement: surface all null rows before computing anything.
    print(f"Loaded {len(rows)} row(s). Null actual_spend rows: {len(null_report)}")
    for nr in null_report:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} -> {nr['reason']}")

    results, error = compute_growth(rows, args.ward, args.category, args.growth_type)
    if error:
        print(error, file=sys.stderr)
        raise SystemExit(2)

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    computed = sum(1 for r in results if r["growth_pct"] != "NOT COMPUTED")
    print(f"Done. {len(results)} period row(s) for {args.ward} / {args.category} "
          f"({args.growth_type}); {computed} computed, {len(results) - computed} flagged. -> {args.output}")


if __name__ == "__main__":
    main()

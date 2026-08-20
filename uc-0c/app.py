"""
UC-0C — Number That Looks Right
Implements the enforcement rules in agents.md and the two skills in skills.md.

Failure modes taught: wrong aggregation level, silent null handling, formula
assumption. This implementation refuses to aggregate, refuses to guess a formula,
flags every null instead of skipping it, and prints the formula on every row.

Skills:
  load_dataset   -> read CSV, validate columns, report every null before returning
  compute_growth -> per-period growth for ONE ward + ONE category, formula shown
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = {"MoM", "YoY"}
AGGREGATE_TOKENS = {"all", "*", "total", "aggregate"}


class RefusalError(Exception):
    """Raised when an enforcement rule requires the agent to refuse rather than guess."""


def load_dataset(input_path: str):
    """
    Read the CSV, validate columns, and build a null report before returning rows.
    Returns: (rows, null_report) where null_report is a list of dicts.
    """
    try:
        with open(input_path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            header = reader.fieldnames or []
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in header]
            if missing_cols:
                raise RefusalError(f"Missing required column(s): {', '.join(missing_cols)}")

            rows = []
            null_report = []
            for raw in reader:
                spend_raw = (raw.get("actual_spend") or "").strip()
                if spend_raw == "":
                    actual_spend = None
                    null_report.append({
                        "period": raw.get("period", "").strip(),
                        "ward": raw.get("ward", "").strip(),
                        "category": raw.get("category", "").strip(),
                        "notes": (raw.get("notes") or "").strip() or "(no reason given)",
                    })
                else:
                    try:
                        actual_spend = float(spend_raw)
                    except ValueError:
                        raise RefusalError(
                            f"Malformed actual_spend '{spend_raw}' at period "
                            f"{raw.get('period')} / {raw.get('ward')}; not coercing silently."
                        )
                rows.append({
                    "period": raw.get("period", "").strip(),
                    "ward": raw.get("ward", "").strip(),
                    "category": raw.get("category", "").strip(),
                    "budgeted_amount": (raw.get("budgeted_amount") or "").strip(),
                    "actual_spend": actual_spend,
                    "notes": (raw.get("notes") or "").strip(),
                })
    except OSError as exc:
        raise RefusalError(f"Could not read dataset '{input_path}': {exc}") from exc

    return rows, null_report


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for exactly one ward + one category.
    Returns a list of output-row dicts. Raises RefusalError on any enforcement breach.
    """
    # Enforcement: no aggregation, no guessed formula.
    if not ward or ward.strip().lower() in AGGREGATE_TOKENS:
        raise RefusalError("Refusing to aggregate across wards. Specify exactly one --ward.")
    if not category or category.strip().lower() in AGGREGATE_TOKENS:
        raise RefusalError("Refusing to aggregate across categories. Specify exactly one --category.")
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise RefusalError(
            f"--growth-type must be one of {sorted(SUPPORTED_GROWTH_TYPES)}; "
            f"got '{growth_type}'. Refusing to guess a formula."
        )

    # Filter to the single ward + category, ordered by period.
    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    subset.sort(key=lambda r: r["period"])
    if not subset:
        raise RefusalError(
            f"No rows found for ward '{ward}' and category '{category}'. "
            f"Refusing to return an empty or zero result."
        )

    lag = 1 if growth_type == "MoM" else 12  # YoY compares to 12 periods earlier
    by_period = {r["period"]: r for r in subset}
    periods = [r["period"] for r in subset]

    output = []
    for idx, period in enumerate(periods):
        current = by_period[period]
        cmp_idx = idx - lag
        cmp_period = periods[cmp_idx] if 0 <= cmp_idx < len(periods) else None
        cmp_row = by_period.get(cmp_period) if cmp_period else None

        base = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": "" if current["actual_spend"] is None else current["actual_spend"],
            "compare_period": cmp_period or "",
            "compare_spend": "",
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "",
            "flag": "",
        }

        # Enforcement: null current or missing/null comparison -> NOT COMPUTED, with reason.
        if current["actual_spend"] is None:
            base["flag"] = "NOT COMPUTED"
            base["formula"] = "n/a — actual_spend is null"
            base["growth_pct"] = "NULL: " + (current["notes"] or "no reason given")
            output.append(base)
            continue
        if cmp_row is None:
            base["flag"] = "N/A"
            base["formula"] = f"n/a — no {growth_type} comparison period available"
            output.append(base)
            continue
        if cmp_row["actual_spend"] is None:
            base["flag"] = "NOT COMPUTED"
            base["compare_spend"] = ""
            base["formula"] = f"n/a — comparison period {cmp_period} is null"
            base["growth_pct"] = "NULL comparison: " + (cmp_row["notes"] or "no reason given")
            output.append(base)
            continue

        cur_val = current["actual_spend"]
        prev_val = cmp_row["actual_spend"]
        growth = (cur_val - prev_val) / prev_val * 100.0
        base["compare_spend"] = prev_val
        base["growth_pct"] = f"{growth:+.1f}%"
        base["formula"] = f"({cur_val} - {prev_val}) / {prev_val} * 100"
        output.append(base)

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exactly one ward, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", help="Exactly one category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        rows, null_report = load_dataset(args.input)

        # Report every null up front (README: report null count and which rows).
        print(f"Null report: {len(null_report)} null actual_spend row(s) in dataset.")
        for n in null_report:
            print(f"  NULL {n['period']} | {n['ward']} | {n['category']} -> {n['notes']}")

        result = compute_growth(rows, args.ward, args.category, args.growth_type)
    except RefusalError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)

    fieldnames = ["ward", "category", "period", "actual_spend", "compare_period",
                  "compare_spend", "growth_type", "growth_pct", "formula", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    computed = sum(1 for r in result if r["flag"] == "")
    not_computed = sum(1 for r in result if r["flag"] == "NOT COMPUTED")
    print(f"Done. {len(result)} periods for {args.ward} / {args.category} "
          f"({computed} computed, {not_computed} flagged null). Written to {args.output}")


if __name__ == "__main__":
    main()

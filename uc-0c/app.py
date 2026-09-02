"""
UC-0C — Budget Growth

Deterministic, per-period budget-growth reporting for exactly ONE ward and ONE
category at a time. Enforces the contract in agents.md / skills.md:

  * Computes month-over-month (MoM) growth only from non-null consecutive
    values, one row per month, and shows the exact formula with real numbers in
    every computed row (e.g. "(19.7 - 14.8) / 14.8 * 100").
  * Refuses (emits no growth numbers) when ward or category is missing, empty,
    or "all"/wildcard — it never aggregates across wards or categories.
  * Refuses when growth_type is not specified — it never silently picks a
    formula.
  * Flags every null actual_spend row as NOT_COMPUTED with the reason from the
    notes column, and also flags the month immediately after a null (whose prior
    value is null). Nulls are never imputed, interpolated, or treated as zero.
  * YoY is an accepted growth_type but is always reported NOT_COMPUTED
    ("no prior-year data") because the dataset covers 2024 only — never guessed.

No runtime LLM — this is deterministic arithmetic, so every guarantee is a
verifiable string/number check. See README.md for the run command.
"""
import argparse
import csv
import os

REQUIRED_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend", "notes",
]

# ward/category values that mean "not a single specific slice" — these must be
# refused because they imply cross-ward or cross-category aggregation.
WILDCARDS = frozenset(["", "all", "*", "%", "any", "everything"])

VALID_GROWTH_TYPES = ("MoM", "YoY")


class GrowthRefusal(Exception):
    """Raised when the request violates the single-ward/single-category or
    explicit-growth-type contract. Carries a human-readable refusal message and
    no growth numbers are produced."""


def load_dataset(input_path):
    """Read the ward budget CSV, validate its columns, and report null
    actual_spend rows before returning the data.

    Returns (rows, null_report):
      * rows — list of dicts (one per CSV row) in period order, each preserving
        period, ward, category, budgeted_amount, actual_spend (float or None),
        actual_spend_raw (original string) and notes. A blank actual_spend is
        kept as None (null marker), never coerced to 0 or skipped.
      * null_report — list of dicts {period, ward, category, reason} for every
        row whose actual_spend is blank, with the reason taken from notes.

    Raises FileNotFoundError if the file is missing and ValueError if a required
    column is absent — before any computation begins.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError("Input CSV not found: %s" % input_path)

    rows = []
    null_report = []
    with open(input_path, newline="", encoding="utf-8-sig") as fin:
        reader = csv.DictReader(fin)
        header = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing:
            raise ValueError(
                "Input CSV is missing required column(s): %s" % ", ".join(missing)
            )

        for raw in reader:
            period = (raw.get("period") or "").strip()
            ward = (raw.get("ward") or "").strip()
            category = (raw.get("category") or "").strip()
            budgeted = (raw.get("budgeted_amount") or "").strip()
            actual_raw = (raw.get("actual_spend") or "").strip()
            notes = (raw.get("notes") or "").strip()

            actual = float(actual_raw) if actual_raw else None
            if actual is None:
                # Preserve the null; report it with its reason from notes.
                null_report.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "reason": notes or "no reason given in notes",
                })

            rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "actual_spend_raw": actual_raw,
                "notes": notes,
            })

    # Period order so consecutive-month growth can be computed reliably.
    rows.sort(key=lambda r: r["period"])
    return rows, null_report


def _is_wildcard(value):
    return value is None or value.strip().lower() in WILDCARDS


def _fmt_pct(value):
    """Format a growth percentage with an explicit sign, 1 decimal place."""
    if value == 0:
        value = 0.0
    return "%+.1f%%" % value


def compute_growth(ward, category, growth_type, rows):
    """Compute per-period growth for a single ward + category, showing the
    formula per row and flagging nulls — or refuse.

    Returns a list of per-period result dicts with fields: period, ward,
    category, actual_spend, growth_type, growth_pct (or "NOT_COMPUTED"),
    formula, flag, reason.

    Raises GrowthRefusal (no numbers produced) if ward or category is missing,
    empty, or "all"/wildcard, or if growth_type is not supplied. Marks
    NOT_COMPUTED (with a reason) for the first month, any null actual_spend row,
    and any month immediately after a null. YoY is always NOT_COMPUTED
    ("no prior-year data") because the dataset is 2024 only.
    """
    if _is_wildcard(ward):
        raise GrowthRefusal(
            "Refusing: a specific --ward is required. This agent computes growth "
            "for exactly one ward and one category — it never aggregates across "
            "wards. Re-run with an exact ward name (e.g. \"Ward 1 – Kasba\")."
        )

    if _is_wildcard(category):
        raise GrowthRefusal(
            "Refusing: a specific --category is required. This agent computes "
            "growth for exactly one ward and one category — it never aggregates "
            "across categories. Re-run with an exact category "
            "(e.g. \"Roads & Pothole Repair\")."
        )

    if growth_type is None or not str(growth_type).strip():
        raise GrowthRefusal(
            "Refusing: --growth-type must be specified explicitly (MoM or YoY). "
            "This agent never picks a growth formula for you."
        )

    growth_type = growth_type.strip()
    match = next((g for g in VALID_GROWTH_TYPES if g.lower() == growth_type.lower()), None)
    if match is None:
        raise GrowthRefusal(
            "Refusing: --growth-type must be one of %s, got %r."
            % (" or ".join(VALID_GROWTH_TYPES), growth_type)
        )
    growth_type = match

    # Filter to exactly this ward + category, in period order.
    slice_rows = [
        r for r in rows
        if r["ward"].lower() == ward.strip().lower()
        and r["category"].lower() == category.strip().lower()
    ]
    if not slice_rows:
        raise GrowthRefusal(
            "Refusing: no rows found for ward %r and category %r. Check the exact "
            "spelling (ward names use an en-dash, e.g. \"Ward 1 – Kasba\")."
            % (ward, category)
        )

    results = []
    prev = None  # previous row in period order
    for row in slice_rows:
        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend_raw"],
            "growth_type": growth_type,
            "growth_pct": "NOT_COMPUTED",
            "formula": "",
            "flag": "",
            "reason": "",
        }

        if growth_type == "YoY":
            # Single-year (2024) dataset: no prior-year value exists. Never guessed.
            result["flag"] = "NOT_COMPUTED"
            result["reason"] = "no prior-year data (dataset covers 2024 only)"
            results.append(result)
            prev = row
            continue

        # MoM from here on.
        if row["actual_spend"] is None:
            # The null row itself — reason from its notes column.
            result["flag"] = "NOT_COMPUTED"
            result["reason"] = "actual_spend is null (%s)" % (
                row["notes"] or "no reason given in notes"
            )
        elif prev is None:
            # First month in range — nothing to compare against.
            result["flag"] = "NOT_COMPUTED"
            result["reason"] = "first month in range — no prior period to compare"
        elif prev["actual_spend"] is None:
            # Month immediately after a null — its prior value is null.
            result["flag"] = "NOT_COMPUTED"
            result["reason"] = (
                "previous month %s actual_spend is null — cannot compute growth"
                % prev["period"]
            )
        else:
            cur_val = row["actual_spend"]
            prev_val = prev["actual_spend"]
            growth = round((cur_val - prev_val) / prev_val * 100, 1)
            result["growth_pct"] = _fmt_pct(growth)
            result["formula"] = "(%s - %s) / %s * 100" % (
                row["actual_spend_raw"], prev["actual_spend_raw"], prev["actual_spend_raw"]
            )

        results.append(result)
        prev = row

    return results


def _write_output(results, output_path):
    fieldnames = [
        "period", "ward", "category", "actual_spend", "growth_type",
        "growth_pct", "formula", "flag", "reason",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    # ward / category / growth-type are intentionally NOT required at the argparse
    # level: their absence must trigger the agent's refusal, not a usage error.
    parser.add_argument("--ward", default=None, help="Exact ward name (single ward only)")
    parser.add_argument("--category", default=None, help="Exact category (single category only)")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY (must be specified explicitly)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)

    print("Loaded %d row(s) from %s." % (len(rows), args.input))
    print("Null actual_spend rows: %d" % len(null_report))
    for item in null_report:
        print("  - %s | %s | %s -> %s"
              % (item["period"], item["ward"], item["category"], item["reason"]))
    print()

    try:
        results = compute_growth(args.ward, args.category, args.growth_type, rows)
    except GrowthRefusal as exc:
        print("REFUSED: %s" % exc)
        return 1

    _write_output(results, args.output)

    computed = sum(1 for r in results if r["growth_pct"] != "NOT_COMPUTED")
    not_computed = len(results) - computed
    print("Wrote %d row(s) for %s / %s (%s) -> %s"
          % (len(results), args.ward, args.category, results[0]["growth_type"], args.output))
    print("  computed: %d | NOT_COMPUTED: %d" % (computed, not_computed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

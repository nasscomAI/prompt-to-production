"""
UC-0C — Number That Looks Right

Per-ward, per-category growth on municipal budget actuals.

The failure this guards against is not a wrong number. It is a RIGHT-LOOKING
number: one aggregated percentage, computed with a formula nobody chose, over a
dataset with five holes in it that were silently skipped. Such a number is
operationally useless and completely convincing, which is the worst combination.

So this tool refuses more than it computes:
  * it will not aggregate across wards or categories;
  * it will not pick MoM or YoY for you;
  * it will not impute, interpolate, or zero-fill a missing actual_spend;
  * it will not invent a 2023 base period that the dataset does not contain;
  * it will not divide by zero and call the result growth.
Every row it does emit carries the substituted formula that produced it.

Run:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 – Kasba" \
                  --category "Roads & Pothole Repair" \
                  --growth-type MoM \
                  --output growth_output.csv
"""
import argparse
import csv
import io
import os
import sys
from typing import Dict, List, Optional

REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount", "actual_spend", "notes")

OUTPUT_FIELDS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "prior_period",
    "prior_actual_spend",
    "growth_type",
    "growth_pct",
    "formula",
    "flag",
    "null_reason",
)

VALID_GROWTH_TYPES = ("MoM", "YoY")

# Tokens that mean "collapse the scope". Enforcement: these are refused.
AGGREGATE_TOKENS = ("all", "*", "any", "total", "aggregate", "combined", "everything")


def _shift_period(period: str, months_back: int) -> Optional[str]:
    """Return the YYYY-MM that is `months_back` months before `period`."""
    try:
        year_text, month_text = period.split("-")
        year = int(year_text)
        month = int(month_text)
    except (ValueError, AttributeError):
        return None
    if not 1 <= month <= 12:
        return None
    total = year * 12 + (month - 1) - months_back
    if total < 0:
        return None
    return "{0:04d}-{1:02d}".format(total // 12, total % 12 + 1)


def _parse_number(value) -> Optional[float]:
    """Parse a spend figure. Blank -> None. Non-numeric -> raises ValueError."""
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text == "":
        return None
    return float(text)


def load_dataset(path: str) -> dict:
    """Read the CSV, validate columns, and report nulls BEFORE any computation."""
    if not os.path.isfile(path):
        print("Error: input file not found: {0}".format(path), file=sys.stderr)
        sys.exit(1)

    try:
        with io.open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                print("Error: input CSV has no header row.", file=sys.stderr)
                sys.exit(1)
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                print(
                    "Error: input CSV is missing required column(s): {0}".format(
                        ", ".join(missing)),
                    file=sys.stderr,
                )
                sys.exit(1)
            rows = list(reader)
    except (IOError, OSError, csv.Error, UnicodeDecodeError) as exc:
        print("Error: could not read {0}: {1}".format(path, exc), file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: {0} contains no data rows. Refusing to report growth over "
              "an empty dataset.".format(path), file=sys.stderr)
        sys.exit(1)

    nulls = []
    invalid = []
    for row in rows:
        raw = (row.get("actual_spend") or "").strip()
        if raw == "":
            nulls.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "reason": (row.get("notes") or "").strip() or "no reason given in notes",
                }
            )
            continue
        try:
            _parse_number(raw)
        except ValueError:
            invalid.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "value": raw,
                }
            )

    # ── Null report. Printed here, before any number is computed. ────────────
    print("=" * 78)
    print("NULL REPORT — read this before reading any growth number")
    print("=" * 78)
    print("Rows loaded: {0} | null actual_spend: {1} | non-numeric actual_spend: {2}".format(
        len(rows), len(nulls), len(invalid)))
    if nulls:
        for item in nulls:
            print("  NULL  {period}  {ward}  {category}".format(**item))
            print("        reason (from notes): {0}".format(item["reason"]))
    else:
        print("  No null actual_spend values found.")
    for item in invalid:
        print("  NON-NUMERIC  {period}  {ward}  {category}  value={value!r}".format(**item))
    print("")

    return {
        "rows": rows,
        "wards": sorted(set(r["ward"] for r in rows)),
        "categories": sorted(set(r["category"] for r in rows)),
        "periods": sorted(set(r["period"] for r in rows)),
        "nulls": nulls,
        "invalid": invalid,
    }


def _refuse(message: str, code: int = 2) -> None:
    """Print a refusal and stop. No output file is written."""
    print("REFUSED: " + message, file=sys.stderr)
    sys.exit(code)


def compute_growth(
    dataset: dict,
    ward: Optional[str],
    category: Optional[str],
    growth_type: str,
) -> List[dict]:
    """Return a per-ward per-category per-period growth table."""
    if growth_type not in VALID_GROWTH_TYPES:
        _refuse("growth type {0!r} is not one of {1}.".format(
            growth_type, ", ".join(VALID_GROWTH_TYPES)))

    # Enforcement: an explicit request to collapse scope is refused, not honoured.
    for label, value in (("--ward", ward), ("--category", category)):
        if value is not None and value.strip().lower() in AGGREGATE_TOKENS:
            _refuse(
                "{0}={1!r} asks for aggregation across {2}s. This tool reports "
                "per-ward per-category figures only — a single combined growth "
                "number hides which ward and which service actually moved, and is "
                "operationally useless. Omit {0} to get every {2} computed "
                "separately.".format(label, value, label.strip("-")))

    if ward is not None and ward not in dataset["wards"]:
        print("Error: unknown ward {0!r}. Valid wards:".format(ward), file=sys.stderr)
        for name in dataset["wards"]:
            print("  {0}".format(name), file=sys.stderr)
        sys.exit(1)
    if category is not None and category not in dataset["categories"]:
        print("Error: unknown category {0!r}. Valid categories:".format(category),
              file=sys.stderr)
        for name in dataset["categories"]:
            print("  {0}".format(name), file=sys.stderr)
        sys.exit(1)

    # Index by scope triple so a prior period is looked up within the SAME
    # ward and category — never across them.
    index = {}
    for row in dataset["rows"]:
        index[(row["ward"], row["category"], row["period"])] = row

    months_back = 1 if growth_type == "MoM" else 12

    selected = [
        r for r in dataset["rows"]
        if (ward is None or r["ward"] == ward)
        and (category is None or r["category"] == category)
    ]

    results = []
    for row in sorted(selected, key=lambda r: (r["ward"], r["category"], r["period"])):
        period = row["period"]
        prior_period = _shift_period(period, months_back)
        prior_row = index.get((row["ward"], row["category"], prior_period)) if prior_period else None

        out = {
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": (row.get("budgeted_amount") or "").strip(),
            "actual_spend": (row.get("actual_spend") or "").strip(),
            "prior_period": prior_period or "",
            "prior_actual_spend": "",
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "",
            "flag": "",
            "null_reason": "",
        }

        try:
            current = _parse_number(row.get("actual_spend"))
        except ValueError:
            out["flag"] = "INVALID_NUMBER"
            out["formula"] = "not computed: actual_spend {0!r} is not a number".format(
                (row.get("actual_spend") or "").strip())
            results.append(out)
            continue

        # This period's value is missing — never imputed, never zero-filled.
        if current is None:
            out["flag"] = "NULL_ACTUAL_SPEND"
            out["null_reason"] = (row.get("notes") or "").strip() or "no reason given in notes"
            out["formula"] = ("not computed: actual_spend is null for this period; "
                              "null is not treated as zero")
            results.append(out)
            continue

        # No base period exists in the dataset at all.
        if prior_row is None:
            if growth_type == "YoY":
                out["flag"] = "NO_PRIOR_YEAR_DATA"
                out["formula"] = (
                    "not computed: YoY needs {0}, which is not in this dataset "
                    "(coverage is 2024-01 to 2024-12); no base period is invented".format(
                        prior_period or "the prior year period"))
            else:
                out["flag"] = "NO_PRIOR_PERIOD"
                out["formula"] = (
                    "not computed: {0} is the first period for this ward and "
                    "category, so there is no base to compare against".format(period))
            results.append(out)
            continue

        try:
            prior = _parse_number(prior_row.get("actual_spend"))
        except ValueError:
            out["flag"] = "INVALID_NUMBER"
            out["formula"] = "not computed: prior period actual_spend is not a number"
            results.append(out)
            continue

        # Base period is missing — again, no imputation and no carry-forward.
        if prior is None:
            out["flag"] = "PRIOR_PERIOD_NULL"
            out["null_reason"] = (prior_row.get("notes") or "").strip() or \
                "no reason given in notes"
            out["formula"] = (
                "not computed: base period {0} has a null actual_spend, and a "
                "missing base is not carried forward".format(prior_period))
            results.append(out)
            continue

        out["prior_actual_spend"] = "{0:g}".format(prior)

        # Percentage growth from zero is undefined, not infinite.
        if prior == 0:
            out["flag"] = "ZERO_BASE_PERIOD"
            out["formula"] = (
                "not computed: base period {0} actual_spend is 0, so percentage "
                "growth is undefined".format(prior_period))
            results.append(out)
            continue

        growth = (current - prior) / prior * 100.0
        out["growth_pct"] = "{0:+.1f}".format(growth)
        out["formula"] = "{0}% = ({1:g} - {2:g}) / {2:g} * 100 = {3:+.1f}".format(
            growth_type, current, prior, growth)
        results.append(out)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Analyser (per-ward, per-category only)")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    parser.add_argument("--ward", default=None,
                        help="Exactly one ward. Omit for every ward computed separately.")
    parser.add_argument("--category", default=None,
                        help="Exactly one category. Omit for every category separately.")
    # Deliberately NOT required and with NO default — see the refusal below.
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY. No default: the tool refuses to guess.")
    parser.add_argument("--aggregate", action="store_true",
                        help="Refused. Present only so the refusal is explicit.")
    args = parser.parse_args()

    if args.aggregate:
        _refuse(
            "--aggregate asks for one number across wards and categories. "
            "A single figure cannot tell an engineer which ward or which service "
            "changed, so this tool does not produce one. Run without --aggregate "
            "to get a per-ward per-category table.")

    # Enforcement: refuse and ASK. Never default to the more common formula.
    if args.growth_type is None:
        print("REFUSED: --growth-type was not specified, and this tool will not "
              "guess it.", file=sys.stderr)
        print("", file=sys.stderr)
        print("  The choice changes the meaning of every number in the table:",
              file=sys.stderr)
        print("    MoM  month-on-month — this period against the month before it.",
              file=sys.stderr)
        print("    YoY  year-on-year   — this period against the same month last "
              "year. Note this dataset covers 2024 only, so every YoY row will "
              "correctly report NO_PRIOR_YEAR_DATA.", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Re-run with --growth-type MoM or --growth-type YoY.", file=sys.stderr)
        sys.exit(2)

    if args.growth_type not in VALID_GROWTH_TYPES:
        _refuse("--growth-type {0!r} is not valid. Use MoM or YoY.".format(args.growth_type))

    # Refuse a scope-collapsing request before doing any work, so the null report
    # for a dataset we are never going to compute is not printed. compute_growth
    # keeps the same guard for callers that use it directly.
    for label, value in (("--ward", args.ward), ("--category", args.category)):
        if value is not None and value.strip().lower() in AGGREGATE_TOKENS:
            _refuse(
                "{0}={1!r} asks for aggregation across {2}s. This tool reports "
                "per-ward per-category figures only. Omit {0} to get every {2} "
                "computed separately.".format(label, value, label.strip("-")))

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    scope_ward = args.ward or "every ward (each computed separately)"
    scope_category = args.category or "every category (each computed separately)"
    in_scope = len([
        r for r in dataset["rows"]
        if (args.ward is None or r["ward"] == args.ward)
        and (args.category is None or r["category"] == args.category)
    ])
    if len(results) != in_scope:
        print("Error: row count mismatch — {0} rows in scope, {1} emitted.".format(
            in_scope, len(results)), file=sys.stderr)
        sys.exit(1)

    try:
        with io.open(args.output, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_FIELDS))
            writer.writeheader()
            writer.writerows(results)
    except (IOError, OSError) as exc:
        print("Error: could not write {0}: {1}".format(args.output, exc), file=sys.stderr)
        sys.exit(1)

    computed = [r for r in results if r["growth_pct"]]
    flags = {}
    for row in results:
        if row["flag"]:
            flags[row["flag"]] = flags.get(row["flag"], 0) + 1

    print("=" * 78)
    print("SCOPE — no figure below is aggregated across wards or categories")
    print("=" * 78)
    print("  Ward     : {0}".format(scope_ward))
    print("  Category : {0}".format(scope_category))
    print("  Growth   : {0}".format(args.growth_type))
    print("  Rows in scope {0} -> rows emitted {1} | computed {2} | not computed {3}".format(
        in_scope, len(results), len(computed), len(results) - len(computed)))
    if flags:
        print("  Flags: " + " | ".join(
            "{0}={1}".format(k, flags[k]) for k in sorted(flags)))
    print("\nGrowth table written to {0}".format(args.output))


if __name__ == "__main__":
    main()

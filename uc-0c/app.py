"""
UC-0C — Number That Looks Right
Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

The naive prompt ("Calculate growth from the data.") returned one line:
"Overall growth: +12.4%". One number, for 300 rows spanning 5 wards, 5
categories and 12 months, with no formula, no scope, and no mention that 5 rows
have no actual_spend at all. It looked right. It was unusable.

Everything in this file exists to make that output impossible:

  scope       every row carries its own ward, category and period; there is no
              code path that sums across wards or categories
  nulls       the 5 blank rows are listed BEFORE any arithmetic runs, with the
              reason from the notes column, and are never filled or skipped
  formula     every row prints the arithmetic with the real operands in it
  no guessing --growth-type has no default; without it the tool refuses

Run:
  python app.py --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
    --growth-type MoM --output growth_output.csv

Full per-ward per-category table (25 scopes, still no aggregation):
  python app.py --input ../data/budget/ward_budget.csv \
    --all-scopes --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes")

OUTPUT_COLUMNS = ("ward", "category", "period", "budgeted_amount",
                  "actual_spend", "prior_period", "prior_actual",
                  "growth_type", "formula", "growth_pct", "status", "note")

GROWTH_TYPES = ("MoM", "YoY")

# Enforcement rule 1 — anything that means "all of them at once" is a request
# to aggregate, and aggregation is refused rather than silently performed.
AGGREGATION_TOKENS = {"all", "*", "total", "totals", "combined", "overall",
                      "everything", "citywide", "city-wide", "aggregate", "sum"}

STATUS_COMPUTED = "COMPUTED"
STATUS_NULL_ACTUAL = "NULL_ACTUAL"
STATUS_PRIOR_NULL = "PRIOR_NULL"
STATUS_NO_PRIOR = "NO_PRIOR_PERIOD"

EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_INPUT_ERROR = 3


def _normalise_dashes(value: str) -> str:
    """Ward names in the source use an en dash; a hyphen typed on the CLI is
    the same ward, so match on a normalised form without rewriting the data."""
    return (value or "").replace("–", "-").replace("—", "-").strip()


def _to_float(raw):
    text = (raw or "").strip()
    if text == "":
        return None, None
    try:
        return float(text), None
    except ValueError:
        return None, "unparseable value: %r" % raw


def load_dataset(path: str) -> dict:
    """Read the CSV, validate columns, and report every null before returning."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                raise ValueError(
                    "Input is missing required column(s): %s. Found: %s"
                    % (", ".join(missing), ", ".join(fieldnames) or "none"))
            raw_rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError("Budget CSV not found at: %s" % path)

    rows, nulls = [], []
    for raw in raw_rows:
        budgeted, budget_error = _to_float(raw.get("budgeted_amount"))
        actual, actual_error = _to_float(raw.get("actual_spend"))
        row = {
            "period": (raw.get("period") or "").strip(),
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "notes": (raw.get("notes") or "").strip(),
        }
        rows.append(row)

        if actual is None:
            nulls.append({
                "period": row["period"], "ward": row["ward"],
                "category": row["category"],
                # Enforcement rule 2 — the reason comes from the notes column,
                # never from the agent's imagination.
                "notes": actual_error or row["notes"] or "(no reason given in notes column)",
            })
        elif budget_error:
            nulls.append({"period": row["period"], "ward": row["ward"],
                          "category": row["category"],
                          "notes": "budgeted_amount " + budget_error})

    return {
        "rows": rows,
        "wards": sorted({r["ward"] for r in rows}),
        "categories": sorted({r["category"] for r in rows}),
        "periods": sorted({r["period"] for r in rows}),
        "nulls": nulls,
        "row_count": len(rows),
    }


def print_null_report(dataset: dict) -> None:
    """Enforcement rule 2: this runs BEFORE any arithmetic."""
    print("NULL REPORT (printed before any growth is computed)")
    print("  rows read: %d | rows with no actual_spend: %d"
          % (dataset["row_count"], len(dataset["nulls"])))
    if not dataset["nulls"]:
        print("  none")
    for null in dataset["nulls"]:
        print("  %s | %s | %s | reason from notes: %s"
              % (null["period"], null["ward"], null["category"], null["notes"]))
    print("  These rows are reported, not filled. A blank actual_spend is not "
          "zero and is not replaced by budgeted_amount.")
    print()


def _prior_period(period: str, growth_type: str) -> str:
    year, month = period.split("-")
    year, month = int(year), int(month)
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    else:  # YoY
        year -= 1
    return "%04d-%02d" % (year, month)


def compute_growth(dataset: dict, ward: str, category: str,
                   growth_type: str) -> list:
    """Per-period table for exactly one ward and one category."""
    if growth_type not in GROWTH_TYPES:
        raise ValueError("growth_type must be one of %s; no default exists."
                         % ", ".join(GROWTH_TYPES))

    ward_key = _normalise_dashes(ward).lower()
    category_key = _normalise_dashes(category).lower()

    scope = [r for r in dataset["rows"]
             if _normalise_dashes(r["ward"]).lower() == ward_key
             and _normalise_dashes(r["category"]).lower() == category_key]

    if not scope:
        raise ValueError(
            "No rows for ward=%r category=%r. An empty table would read as "
            "zero growth, so this is an error.\n  Valid wards: %s\n  "
            "Valid categories: %s"
            % (ward, category, " | ".join(dataset["wards"]),
               " | ".join(dataset["categories"])))

    by_period = {r["period"]: r for r in scope}
    results = []

    for period in sorted(by_period):
        row = by_period[period]
        prior_key = _prior_period(period, growth_type)
        prior = by_period.get(prior_key)

        result = {
            "ward": row["ward"],
            "category": row["category"],
            "period": period,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": "" if row["actual_spend"] is None else row["actual_spend"],
            "prior_period": prior_key if prior else "",
            "prior_actual": "",
            "growth_type": growth_type,
            "formula": "",
            "growth_pct": "",
            "status": "",
            "note": row["notes"],
        }

        if row["actual_spend"] is None:
            result["status"] = STATUS_NULL_ACTUAL
            result["formula"] = ("not computed — actual_spend is blank for this "
                                 "period")
            result["note"] = row["notes"] or "(no reason given in notes column)"
        elif prior is None:
            result["status"] = STATUS_NO_PRIOR
            result["formula"] = ("not computed — no %s comparison period (%s) "
                                 "in this dataset" % (growth_type, prior_key))
        elif prior["actual_spend"] is None:
            result["status"] = STATUS_PRIOR_NULL
            result["formula"] = ("not computed — actual_spend for the "
                                 "comparison period %s is blank" % prior_key)
            result["note"] = (prior["notes"] or "(no reason given in notes column)") \
                + " [reason belongs to %s]" % prior_key
        elif prior["actual_spend"] == 0.0:
            result["status"] = STATUS_PRIOR_NULL
            result["prior_actual"] = 0.0
            result["formula"] = ("not computed — comparison period %s actual is "
                                 "0.0, percentage growth is undefined" % prior_key)
        else:
            current, previous = row["actual_spend"], prior["actual_spend"]
            growth = (current - previous) / previous * 100.0
            result["status"] = STATUS_COMPUTED
            result["prior_actual"] = previous
            # Enforcement rule 3 — real operands, not the symbolic form.
            result["formula"] = ("%s %% = (%.1f - %.1f) / %.1f x 100"
                                 % (growth_type, current, previous, previous))
            result["growth_pct"] = "%+.1f" % growth

        results.append(result)

    return results


def _refuse(message: str) -> int:
    print("REFUSED: " + message, file=sys.stderr)
    print("No output file was written.", file=sys.stderr)
    return EXIT_REFUSED


def main() -> int:
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    parser.add_argument("--ward", help="Exact ward value from the file")
    parser.add_argument("--category", help="Exact category value from the file")
    # No default and no choices= here on purpose: argparse rejecting the value
    # would hide the refusal behind a usage error. The refusal is ours to make.
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY — required, never inferred")
    parser.add_argument("--all-scopes", action="store_true",
                        help="Emit every ward x category pair as separate rows. "
                             "This is not aggregation — nothing is summed.")
    parser.add_argument("--aggregate", action="store_true",
                        help="Always refused; kept so the refusal is testable.")
    args = parser.parse_args()

    # ---- Enforcement rule 4: refuse and ask, never guess --------------------
    if not args.growth_type:
        return _refuse(
            "--growth-type was not specified. This dataset is monthly, but "
            "'monthly data' is not a reason to assume you wanted MoM.\n"
            "  Choose one and re-run: --growth-type MoM  or  --growth-type YoY")
    if args.growth_type not in GROWTH_TYPES:
        return _refuse("--growth-type %r is not recognised. Choose MoM or YoY."
                       % args.growth_type)

    # ---- Enforcement rule 1: refuse aggregation ----------------------------
    if args.aggregate:
        return _refuse(
            "cross-ward / cross-category aggregation was requested.\n"
            "  agents.md enforcement rule 1: never aggregate across wards or "
            "categories.\n"
            "  A single citywide growth number hides 5 wards, 5 categories and "
            "5 missing months behind one figure.\n"
            "  Use --all-scopes to get every ward x category pair as its own "
            "separate rows instead.")
    for flag, value in (("--ward", args.ward), ("--category", args.category)):
        if value and value.strip().lower() in AGGREGATION_TOKENS:
            return _refuse(
                "%s=%r asks for every scope combined into one figure.\n"
                "  agents.md enforcement rule 1: never aggregate across wards "
                "or categories.\n"
                "  Use --all-scopes for a per-ward per-category table."
                % (flag, value))

    if not args.all_scopes and not (args.ward and args.category):
        return _refuse(
            "both --ward and --category are required so that every output row "
            "has a scope.\n  Pass --all-scopes to compute all 25 ward x "
            "category pairs separately.")

    # ---- Load and report nulls before any arithmetic -----------------------
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print("INPUT ERROR: %s" % exc, file=sys.stderr)
        return EXIT_INPUT_ERROR

    print_null_report(dataset)

    if args.all_scopes:
        scopes = [(w, c) for w in dataset["wards"] for c in dataset["categories"]]
    else:
        scopes = [(args.ward, args.category)]

    rows = []
    try:
        for ward, category in scopes:
            rows.extend(compute_growth(dataset, ward, category, args.growth_type))
    except ValueError as exc:
        print("INPUT ERROR: %s" % exc, file=sys.stderr)
        return EXIT_INPUT_ERROR

    computed = sum(1 for r in rows if r["status"] == STATUS_COMPUTED)

    # ---- Enforcement rule 6: a table of nothing is not a result ------------
    if computed == 0:
        return _refuse(
            "%s growth could not be computed for a single row in this dataset "
            "(periods present: %s .. %s).\n"
            "  Writing %d rows with every growth value blank would look like "
            "output and contain nothing.\n"
            "  For a dataset covering one year, use --growth-type MoM."
            % (args.growth_type, dataset["periods"][0], dataset["periods"][-1],
               len(rows)))

    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)

    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    print("SCOPES: %d (each row is one ward + one category + one period; "
          "nothing is summed across scopes)" % len(scopes))
    print("ROWS WRITTEN: %d" % len(rows))
    for status in (STATUS_COMPUTED, STATUS_NULL_ACTUAL, STATUS_PRIOR_NULL,
                   STATUS_NO_PRIOR):
        print("  %-16s %d" % (status, counts.get(status, 0)))
    print("Written to %s" % args.output)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

"""
UC-0C — Number That Looks Right

Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

A single growth percentage for "the budget" is the failure this UC exists to
prevent: it looks authoritative, it is arithmetically defensible, and no
official can act on it because it belongs to no one. So this tool has no code
path that sums across wards or categories, refuses when the method is
unspecified, and prints the substituted arithmetic beside every figure.

Run:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 - Kasba" \
                  --category "Roads & Pothole Repair" \
                  --growth-type MoM \
                  --output growth_output.csv

Omit --ward/--category to emit every (ward, category) series separately --
25 independent series, never a combined figure.
"""
import argparse
import csv
import os
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]

OUTPUT_FIELDS = ["ward", "category", "period", "budgeted_amount",
                 "actual_spend", "prior_period", "prior_actual_spend",
                 "growth_type", "formula", "growth_pct", "status", "note"]

STATUS_OK = "COMPUTED"
STATUS_NO_PRIOR = "NO_PRIOR_PERIOD"
STATUS_NULL_CURRENT = "NOT_COMPUTED_NULL_CURRENT"
STATUS_NULL_PRIOR = "NOT_COMPUTED_PRIOR_NULL"
STATUS_ZERO_BASE = "NOT_COMPUTED_ZERO_BASE"
STATUS_NO_PRIOR_YEAR = "NOT_COMPUTED_NO_PRIOR_YEAR"


def _normalise(value):
    """Collapse dash variants and whitespace.

    'Ward 1 - Kasba' and 'Ward 1 - Kasba' with an en dash are the same ward
    typed on two keyboards. This is a formatting equivalence, not a fuzzy
    match: no closest-match selection is ever performed (enforcement rule 5).
    """
    if value is None:
        return ""
    text = re.sub(r"[‐-―−]", "-", str(value))
    return re.sub(r"\s+", " ", text).strip().lower()


def load_dataset(path):
    """Read the CSV, validate columns, and report nulls before returning."""
    if not os.path.isfile(path):
        raise SystemExit("ERROR: input file not found: %s" % path)
    try:
        handle = open(path, "r", newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise SystemExit("ERROR: cannot read %s (%s)" % (path, exc))

    with handle:
        reader = csv.DictReader(handle)
        found = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in found]
        if missing:
            raise SystemExit(
                "ERROR: input is missing required column(s): %s. Columns "
                "found: %s" % (", ".join(missing), ", ".join(found) or "(none)")
            )
        raw_rows = list(reader)

    if not raw_rows:
        raise SystemExit(
            "ERROR: %s contains no data rows — refusing to emit an empty "
            "growth table that would look clean." % path
        )

    rows = []
    null_rows = []
    seen_keys = {}
    duplicates = []

    for raw in raw_rows:
        period = (raw.get("period") or "").strip()
        ward = (raw.get("ward") or "").strip()
        category = (raw.get("category") or "").strip()
        note = (raw.get("notes") or "").strip()
        spend_raw = (raw.get("actual_spend") or "").strip()
        budget_raw = (raw.get("budgeted_amount") or "").strip()

        # Enforcement rule 2: a null is None, never 0.0, never backfilled
        # from budgeted_amount.
        if spend_raw == "":
            actual = None
            null_rows.append({"period": period, "ward": ward,
                              "category": category,
                              "note": note or "(no reason given in notes)"})
        else:
            try:
                actual = float(spend_raw)
            except ValueError:
                actual = None
                null_rows.append({"period": period, "ward": ward,
                                  "category": category,
                                  "note": "unparseable value: %r" % spend_raw})
        try:
            budgeted = float(budget_raw) if budget_raw else None
        except ValueError:
            budgeted = None

        key = (period, _normalise(ward), _normalise(category))
        if key in seen_keys:
            duplicates.append(key)
            continue
        seen_keys[key] = True

        rows.append({"period": period, "ward": ward, "category": category,
                     "budgeted_amount": budgeted, "actual_spend": actual,
                     "note": note})

    wards = sorted(set(r["ward"] for r in rows))
    categories = sorted(set(r["category"] for r in rows))
    periods = sorted(set(r["period"] for r in rows))

    # Enforcement rule 2: nulls are reported BEFORE any computation.
    print("Input            : %s" % path)
    print("Rows parsed      : %d" % len(rows))
    print("Wards            : %d   Categories: %d   Periods: %s..%s"
          % (len(wards), len(categories), periods[0], periods[-1]))
    if duplicates:
        print("DUPLICATE KEYS   : %d (first occurrence kept; summing them "
              "would be an undeclared aggregation)" % len(duplicates))
    print("")
    print("NULL REPORT — %d row(s) with no usable actual_spend:" % len(null_rows))
    if null_rows:
        for item in null_rows:
            print("  %s | %-24s | %-26s | %s"
                  % (item["period"], item["ward"], item["category"],
                     item["note"]))
    else:
        print("  none")
    print("")

    return {"rows": rows, "wards": wards, "categories": categories,
            "periods": periods, "null_rows": null_rows,
            "duplicates": duplicates}


def _series(dataset, ward, category):
    """Rows for exactly one (ward, category), ordered by period."""
    want_w, want_c = _normalise(ward), _normalise(category)
    picked = [r for r in dataset["rows"]
              if _normalise(r["ward"]) == want_w
              and _normalise(r["category"]) == want_c]
    return sorted(picked, key=lambda r: r["period"])


def _prior_period(period, growth_type):
    year, month = int(period[:4]), int(period[5:7])
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    else:  # YoY
        year -= 1
    return "%04d-%02d" % (year, month)


def compute_growth(dataset, ward, category, growth_type):
    """Per-period growth for ONE ward and ONE category.

    There is deliberately no parameter by which this function could be asked
    to span more than one ward or category (enforcement rule 1).
    """
    if growth_type not in ("MoM", "YoY"):
        raise SystemExit(
            "REFUSED: unsupported --growth-type %r. Supported: MoM, YoY."
            % growth_type)

    series = _series(dataset, ward, category)
    if not series:
        raise SystemExit(
            "REFUSED: no rows for ward %r and category %r — refusing to guess "
            "the closest match.\n  Valid wards     : %s\n  Valid categories: %s"
            % (ward, category, " | ".join(dataset["wards"]),
               " | ".join(dataset["categories"]))
        )

    by_period = {r["period"]: r for r in series}
    coverage = "%s..%s" % (dataset["periods"][0], dataset["periods"][-1])
    results = []

    for row in series:
        period = row["period"]
        prior_key = _prior_period(period, growth_type)
        prior = by_period.get(prior_key)
        current = row["actual_spend"]

        out = {
            "ward": row["ward"],
            "category": row["category"],
            "period": period,
            "budgeted_amount": ("" if row["budgeted_amount"] is None
                                else row["budgeted_amount"]),
            "actual_spend": "" if current is None else current,
            "prior_period": prior_key,
            "prior_actual_spend": "",
            "growth_type": growth_type,
            "formula": "",
            "growth_pct": "",
            "status": "",
            "note": "",
        }

        # Enforcement rule 6: YoY has no operand in a single-year dataset.
        if growth_type == "YoY" and prior is None:
            out["status"] = STATUS_NO_PRIOR_YEAR
            out["formula"] = "(%s - %s_prior_year) / %s_prior_year * 100" % (
                "" if current is None else current, period, period)
            out["note"] = ("dataset covers %s only; no prior-year period %s "
                           "exists. Not falling back to MoM."
                           % (coverage, prior_key))
            results.append(out)
            continue

        if prior is None:
            out["status"] = STATUS_NO_PRIOR
            out["note"] = ("no prior period %s in the dataset (series begins "
                           "at %s)" % (prior_key, series[0]["period"]))
            results.append(out)
            continue

        prior_value = prior["actual_spend"]
        out["prior_actual_spend"] = "" if prior_value is None else prior_value

        # Enforcement rule 3: a null invalidates two rows, and both say so.
        if current is None:
            out["status"] = STATUS_NULL_CURRENT
            out["note"] = ("actual_spend is null for %s — source note: %s"
                           % (period, row["note"] or "(none)"))
        elif prior_value is None:
            out["status"] = STATUS_NULL_PRIOR
            out["note"] = ("prior period %s has null actual_spend — source "
                           "note: %s" % (prior_key, prior["note"] or "(none)"))
        elif prior_value == 0:
            out["status"] = STATUS_ZERO_BASE
            out["note"] = ("prior period %s actual_spend is 0.0; growth "
                           "undefined against a zero base" % prior_key)
        else:
            growth = (current - prior_value) / prior_value * 100.0
            out["status"] = STATUS_OK
            # Enforcement rule 4: substituted operands, not symbols.
            out["formula"] = "(%.1f - %.1f) / %.1f * 100" % (
                current, prior_value, prior_value)
            out["growth_pct"] = round(growth, 1)

        results.append(out)

    return results


def refuse_aggregation(dataset, what):
    raise SystemExit(
        "REFUSED: cross-ward or cross-category aggregation is not permitted by "
        "this agent (%s).\n"
        "  A single blended figure across %d wards and %d categories belongs to "
        "no ward officer and no category owner, so no one can act on it.\n"
        "  Available scope — one ward AND one category per series:\n"
        "    wards     : %s\n"
        "    categories: %s\n"
        "  Re-run with --ward and --category, or omit both to emit all %d "
        "series separately."
        % (what, len(dataset["wards"]), len(dataset["categories"]),
           " | ".join(dataset["wards"]), " | ".join(dataset["categories"]),
           len(dataset["wards"]) * len(dataset["categories"]))
    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write results")
    parser.add_argument("--ward", default=None, help="Exact ward name")
    parser.add_argument("--category", default=None, help="Exact category name")
    # Deliberately NOT required=True: the refusal must come from the agent's
    # own enforcement rule with an explanation, not from an argparse usage
    # error (enforcement rule 5).
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY — no default, must be stated")
    parser.add_argument("--aggregate", action="store_true",
                        help="Request a combined figure (always refused)")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    # Enforcement rule 1: aggregation has no code path, only a refusal.
    if args.aggregate:
        refuse_aggregation(dataset, "--aggregate was requested")
    for name, value in (("--ward", args.ward), ("--category", args.category)):
        if value is not None and _normalise(value) in ("all", "total",
                                                       "overall", "*"):
            refuse_aggregation(dataset, "%s=%r requests every scope at once"
                               % (name, value))

    # Enforcement rule 5: refuse and ask, never guess the method.
    if args.growth_type is None:
        raise SystemExit(
            "REFUSED: --growth-type was not specified and this agent does not "
            "choose one for you.\n"
            "  MoM (month-over-month) and YoY (year-over-year) answer different "
            "questions and would return different numbers from the same rows.\n"
            "  Re-run with --growth-type MoM or --growth-type YoY.\n"
            "  Note: this dataset covers %s..%s, a single calendar year, so YoY "
            "has no prior-year operand for any period."
            % (dataset["periods"][0], dataset["periods"][-1])
        )

    if args.ward is None and args.category is None:
        pairs = [(w, c) for w in dataset["wards"] for c in dataset["categories"]]
        print("No --ward/--category given: emitting all %d series SEPARATELY. "
              "No figure is combined across wards or categories." % len(pairs))
    elif args.ward is None or args.category is None:
        raise SystemExit(
            "REFUSED: --ward and --category must be given together. Supplying "
            "only one implies a total across the other dimension, which this "
            "agent does not compute.\n"
            "  wards     : %s\n  categories: %s"
            % (" | ".join(dataset["wards"]), " | ".join(dataset["categories"]))
        )
    else:
        pairs = [(args.ward, args.category)]

    all_rows = []
    for ward, category in pairs:
        all_rows.extend(compute_growth(dataset, ward, category,
                                       args.growth_type))

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(args.output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    computed = [r for r in all_rows if r["status"] == STATUS_OK]
    blocked = [r for r in all_rows if r["status"] not in (STATUS_OK,)]

    print("GROWTH TABLE — %s" % args.growth_type)
    print("  series emitted   : %d (each one ward x one category)" % len(pairs))
    print("  rows written     : %d" % len(all_rows))
    print("  computed         : %d" % len(computed))
    print("  not computed     : %d" % len(blocked))
    status_counts = {}
    for row in blocked:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    for status in sorted(status_counts):
        print("      %-28s %d" % (status, status_counts[status]))
    print("  aggregated figures emitted: 0 (by construction)")
    print("Written to       : %s" % args.output)


if __name__ == "__main__":
    main()

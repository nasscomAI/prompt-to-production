"""
UC-0C — Number That Looks Right

Reads a ward-level budget CSV and computes infrastructure spend growth for
exactly ONE ward and ONE category at a time, writing a per-period table in
which no number can silently look right. Behaviour follows the enforcement
rules in agents.md:

- scope lock: growth is computed only for the single ward and single
  category named on the command line; all-ward or all-category requests are
  refused, never aggregated
- null flagging: every null actual_spend row is reported with its
  notes-column reason before any computation runs; null rows inside the
  requested scope are flagged FLAGGED_NULL in the output instead of being
  skipped or zero-filled
- formula transparency: every computed row shows the exact formula applied
  next to its result, e.g. (19.7 - 14.8) / 14.8 * 100 = +33.1%
- refusal guard: a missing --growth-type (or an unknown one), a missing
  --ward or --category, a missing input file, or an input missing required
  columns exits non-zero with an explicit refusal and writes no output

The tool is deterministic and fully offline.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

GROWTH_TYPES = {
    "MoM": "MoM growth % = (current - previous month) / previous month * 100",
    "YoY": "YoY growth % = (current - same month previous year) / same month previous year * 100",
}

OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "growth_type",
    "actual_spend_lakh",
    "previous_period",
    "previous_spend_lakh",
    "formula",
    "growth_pct",
    "status",
    "note",
]


class Refusal(Exception):
    pass


def repair_text(value):
    if not value:
        return value
    try:
        return value.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def normalise(value):
    text = repair_text(value)
    for dash in ("\u2013", "\u2014", "\u2012", "\u2212"):
        text = text.replace(dash, "-")
    return " ".join(text.casefold().split())


def load_dataset(path):
    try:
        with open(path, encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise Refusal(
                    "REFUSAL: input file is missing required columns: "
                    + ", ".join(missing)
                )
            rows = [
                {key: repair_text(raw.get(key) or "") for key in REQUIRED_COLUMNS}
                for raw in reader
            ]
    except OSError as error:
        raise Refusal("REFUSAL: cannot read input file {}: {}".format(path, error))
    if not rows:
        raise Refusal("REFUSAL: input file {} contains no data rows".format(path))

    null_rows = []
    for line_number, row in enumerate(rows, start=2):
        if not row["actual_spend"].strip():
            null_rows.append(
                {
                    "line": line_number,
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"].strip() or "(no reason given in notes)",
                }
            )

    print("load_dataset: {} data rows loaded from {}".format(len(rows), path))
    print(
        "load_dataset: NULL REPORT — {} null actual_spend rows found; "
        "flagging before any compute:".format(len(null_rows))
    )
    for entry in null_rows:
        print(
            "  - line {:>3}: {} | {} | {} | reason: {}".format(
                entry["line"],
                entry["period"],
                entry["ward"],
                entry["category"],
                entry["reason"],
            )
        )
    return rows


def compute_growth(rows, ward, category, growth_type):
    scope = [
        row
        for row in rows
        if normalise(row["ward"]) == normalise(ward)
        and normalise(row["category"]) == normalise(category)
    ]
    if not scope:
        raise Refusal(
            "REFUSAL: ward/category pair not found in dataset.\n"
            "  wards available: {}\n"
            "  categories available: {}".format(
                "; ".join(sorted({row["ward"] for row in rows})),
                "; ".join(sorted({row["category"] for row in rows})),
            )
        )

    scope.sort(key=lambda row: row["period"])
    history = {row["period"]: row for row in scope}
    results = []
    for row in scope:
        period = row["period"]
        current = row["actual_spend"].strip()
        note = row["notes"].strip()
        if growth_type == "MoM":
            year, month = int(period[:4]), int(period[5:7])
            previous_period = "{}-{:02d}".format(year if month > 1 else year - 1, month - 1 if month > 1 else 12)
        else:
            previous_period = "{}{}".format(int(period[:4]) - 1, period[4:])
        previous_row = history.get(previous_period)
        previous = previous_row["actual_spend"].strip() if previous_row else ""

        base = {
            "period": period,
            "ward": row["ward"],
            "category": row["category"],
            "growth_type": growth_type,
            "actual_spend_lakh": current,
            "previous_period": previous_period,
            "previous_spend_lakh": previous,
            "note": note,
        }

        if not current:
            results.append(
                dict(
                    base,
                    formula="NOT COMPUTED — actual_spend is NULL",
                    growth_pct="NULL",
                    status="FLAGGED_NULL",
                    note=note or "(no reason given in notes)",
                )
            )
        elif not previous:
            if previous_row is None:
                reason = (
                    "first period — no previous month exists"
                    if growth_type == "MoM"
                    else "no prior-year data in dataset"
                )
                results.append(
                    dict(
                        base,
                        formula="N/A — {}".format(reason),
                        growth_pct="N/A",
                        status="NO_BASELINE",
                    )
                )
            else:
                results.append(
                    dict(
                        base,
                        formula="NOT COMPUTED — previous period actual_spend is NULL",
                        growth_pct="NULL",
                        status="PREVIOUS_NULL",
                        note=previous_row["notes"].strip() or "(no reason given in notes)",
                    )
                )
        else:
            current_value = float(current)
            previous_value = float(previous)
            pct = (current_value - previous_value) / previous_value * 100.0
            formula = "({:g} - {:g}) / {:g} * 100".format(
                current_value, previous_value, previous_value
            )
            results.append(
                dict(
                    base,
                    formula=formula,
                    growth_pct="{:+.1f}%".format(pct),
                    status="COMPUTED",
                )
            )
    return results


def write_output(path, results):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "UC-0C deterministic spend-growth calculator. Computes growth for "
            "one ward and one category only — aggregation requests are refused."
        )
    )
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--ward", help="exact single ward to compute for")
    parser.add_argument("--category", help="exact single category to compute for")
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY — never guessed")
    parser.add_argument("--output", required=True, help="path of the CSV table to write")
    args = parser.parse_args()

    refusals = []
    if not args.ward:
        refusals.append(
            "no --ward was specified. Aggregating across wards would produce one "
            "operationally useless number — refusing."
        )
    if not args.category:
        refusals.append(
            "no --category was specified. Aggregating across categories would "
            "produce one operationally useless number — refusing."
        )
    if not args.growth_type:
        refusals.append(
            "no --growth-type was specified. Never guessing the formula — pass "
            "--growth-type MoM or --growth-type YoY."
        )
    if refusals:
        for message in refusals:
            print("REFUSAL: " + message, file=sys.stderr)
        raise SystemExit(2)

    growth_type = args.growth_type.strip()
    if growth_type not in GROWTH_TYPES:
        print(
            "REFUSAL: unknown --growth-type '{}'. Valid choices: {}. "
            "Never guessing between them.".format(growth_type, ", ".join(GROWTH_TYPES)),
            file=sys.stderr,
        )
        raise SystemExit(2)

    scope_terms = {"all", "*", "total", "combined"}
    if args.ward.strip().casefold() in scope_terms or args.category.strip().casefold() in scope_terms:
        print(
            "REFUSAL: all-ward/all-category aggregation is forbidden by "
            "enforcement rule 1. Name exactly one ward and one category.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, growth_type)
    except Refusal as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
    write_output(args.output, results)

    print("compute_growth: scope = ward '{}' | category '{}' | {}".format(args.ward, args.category, GROWTH_TYPES[growth_type]))
    statuses = {}
    for result in results:
        statuses[result["status"]] = statuses.get(result["status"], 0) + 1
    summary = ", ".join("{}={}".format(status, count) for status, count in sorted(statuses.items()))
    print(
        "compute_growth: wrote {} per-period rows to {} ({})".format(
            len(results), args.output, summary
        )
    )


if __name__ == "__main__":
    main()

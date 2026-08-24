"""
UC-0C — Number That Looks Right

The dangerous output here is not a crash, it is a plausible percentage. A single
city-wide growth figure computed by carrying a value across a missing month will be
quoted in a council meeting and nobody will be able to tell it is wrong by looking at it.

So every row in the output carries its own ward, its own category, and the formula with
operands substituted — a reviewer can re-derive any figure by hand from the row alone.
Nulls are flagged, never imputed. Aggregation is refused, not warned about.

Run (single series, as documented in the UC-0C README):
    python3 app.py --input ../data/budget/ward_budget.csv \
                   --ward "Ward 1 – Kasba" \
                   --category "Roads & Pothole Repair" \
                   --growth-type MoM \
                   --output growth_output.csv

Run (every ward x category series, each row still scoped to one ward and one category):
    python3 app.py --input ../data/budget/ward_budget.csv \
                   --all-series --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]

# Enforcement: these must never be accepted as a ward or category value.
AGGREGATION_TOKENS = {"all", "*", "total", "everything", "any", "combined", "sum",
                      "city", "citywide", "city-wide", "all wards", "all categories"}

OUTPUT_FIELDS = ["ward", "category", "period", "budgeted_amount", "actual_spend",
                 "previous_period", "previous_actual", "growth_pct", "formula",
                 "status", "note"]


def load_dataset(path: str) -> dict:
    """
    Read the CSV, validate columns, and report nulls and which rows before returning.

    A blank actual_spend becomes None — never 0.0. That single choice is the difference
    between "the ward did not submit figures" and "the ward spent nothing".
    """
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            raw_rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        sys.exit(f"ERROR: input file not found: {path}")

    if not raw_rows:
        sys.exit(f"ERROR: no data rows in {path}")

    missing = [c for c in REQUIRED_COLUMNS if c not in raw_rows[0]]
    if missing:
        sys.exit(f"ERROR: {path} is missing required column(s): {', '.join(missing)}\n"
                 f"       columns found: {', '.join(raw_rows[0].keys())}")

    rows, nulls = [], []
    for line_no, raw in enumerate(raw_rows, start=2):
        note = (raw.get("notes") or "").strip()
        actual_text = (raw.get("actual_spend") or "").strip()

        try:
            budgeted = float((raw.get("budgeted_amount") or "").strip())
        except ValueError:
            sys.exit(f"ERROR: {path} line {line_no}: budgeted_amount is not numeric "
                     f"({raw.get('budgeted_amount')!r}). A corrupt budget figure is a "
                     f"file problem, not a missing submission — refusing to continue.")

        if actual_text == "":
            actual = None
        else:
            try:
                actual = float(actual_text)
            except ValueError:
                # Not coerced to 0 — treated as missing, with the raw text preserved.
                actual = None
                note = (f"{note} | unparseable actual_spend {actual_text!r} treated as "
                        f"missing, not zero").strip(" |")

        row = {
            "period": (raw.get("period") or "").strip(),
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "note": note,
        }
        rows.append(row)
        if actual is None:
            nulls.append({
                "period": row["period"], "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted,
                "note": note or "(no reason given in notes column)",
            })

    return {
        "rows": rows,
        "wards": sorted({r["ward"] for r in rows}),
        "categories": sorted({r["category"] for r in rows}),
        "periods": sorted({r["period"] for r in rows}),
        "nulls": nulls,
        "null_count": len(nulls),
    }


def _previous_period(period: str, growth_type: str) -> str:
    """MoM steps back one month; YoY steps back twelve. Purely arithmetic on YYYY-MM."""
    year, month = (int(part) for part in period.split("-"))
    if growth_type == "MoM":
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    else:  # YoY
        year -= 1
    return f"{year:04d}-{month:02d}"


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Per-period growth for exactly ONE ward and ONE category.

    Never reaches past a null to find a usable base: a growth figure whose base is
    missing is flagged, not computed. That is the whole point of this use case.
    """
    if growth_type not in ("MoM", "YoY"):
        sys.exit(f"REFUSED: unrecognised --growth-type {growth_type!r}. "
                 f"Permitted values: MoM, YoY.")

    if ward not in dataset["wards"]:
        sys.exit(f"REFUSED: ward {ward!r} is not present in the data.\n"
                 f"         available wards: {dataset['wards']}")
    if category not in dataset["categories"]:
        sys.exit(f"REFUSED: category {category!r} is not present in the data.\n"
                 f"         available categories: {dataset['categories']}")

    series = {r["period"]: r for r in dataset["rows"]
              if r["ward"] == ward and r["category"] == category}
    if not series:
        sys.exit(f"REFUSED: no rows for ward {ward!r} + category {category!r}. "
                 f"An empty table is not an answer of zero.")

    out = []
    for period in sorted(series):
        row = series[period]
        previous_key = _previous_period(period, growth_type)
        previous = series.get(previous_key)
        actual = row["actual_spend"]

        record = {
            "ward": ward,
            "category": category,
            "period": period,
            "budgeted_amount": f"{row['budgeted_amount']:.1f}",
            "actual_spend": "" if actual is None else f"{actual:.1f}",
            "previous_period": previous_key,
            "previous_actual": "",
            "growth_pct": "",
            "formula": "",
            "status": "",
            "note": row["note"],
        }

        # Enforcement: null actual is flagged with its reason, before any computation.
        if actual is None:
            record["status"] = "NULL_ACTUAL"
            record["formula"] = "not computed — actual_spend missing for this period"
            record["note"] = row["note"] or "(no reason given in notes column)"
            out.append(record)
            continue

        if previous is None:
            # No such period in the data at all (Jan for MoM, all of 2024 for YoY).
            record["status"] = ("INSUFFICIENT_HISTORY" if growth_type == "YoY"
                                else "NO_BASE")
            record["formula"] = (f"not computed — no {previous_key} row exists for this "
                                f"ward and category")
            out.append(record)
            continue

        base = previous["actual_spend"]
        if base is None:
            # Enforcement: never reach further back to find a usable base.
            record["status"] = "NULL_BASE"
            record["previous_actual"] = ""
            record["formula"] = (f"not computed — base period {previous_key} has no "
                                f"actual_spend; growth against a missing base would be "
                                f"fabricated")
            record["note"] = (previous["note"]
                              or f"base period {previous_key} actual_spend missing")
            out.append(record)
            continue

        record["previous_actual"] = f"{base:.1f}"
        if base == 0:
            record["status"] = "NO_BASE"
            record["formula"] = (f"not computed — base period {previous_key} "
                                 f"actual_spend is 0; percentage growth from zero is "
                                 f"undefined")
            out.append(record)
            continue

        growth = (actual - base) / base * 100
        record["growth_pct"] = f"{growth:+.1f}"
        # Enforcement: formula shown with operands substituted, so it re-derives by hand.
        record["formula"] = (f"{growth_type} = ({actual:.1f} - {base:.1f}) / {base:.1f} "
                             f"x 100 = {growth:+.1f}%")
        record["status"] = "OK"
        out.append(record)

    assert len(out) == len(series), "period dropped from output"
    return out


def _refuse_aggregation(args, dataset):
    """
    Enforcement rule 1. Omitting the scope, or naming ALL, is an aggregation request.

    This exits rather than warning, and writes no partial file.
    """
    for flag, value in (("--ward", args.ward), ("--category", args.category)):
        if value is None:
            sys.exit(
                f"REFUSED: {flag} was not specified.\n"
                f"         This tool will not aggregate across wards or categories — a "
                f"single combined\n"
                f"         growth figure hides the per-ward variation that the figure "
                f"is used to decide on.\n"
                f"         Name one explicitly, or pass --all-series to emit every "
                f"ward x category\n"
                f"         series as separately scoped rows.\n"
                f"         wards      : {dataset['wards']}\n"
                f"         categories : {dataset['categories']}"
            )
        if value.strip().lower() in AGGREGATION_TOKENS:
            sys.exit(
                f"REFUSED: {flag}={value!r} is an aggregation request.\n"
                f"         Growth across combined wards or categories is not a figure "
                f"this tool will\n"
                f"         produce. Name one explicitly, or pass --all-series."
            )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C per-ward per-category budget growth calculator")
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="path to growth_output.csv")
    parser.add_argument("--ward", default=None, help="exact ward name (required)")
    parser.add_argument("--category", default=None, help="exact category (required)")
    # Deliberately no default: the user must own which claim they are making.
    parser.add_argument("--growth-type", default=None, choices=["MoM", "YoY"],
                        help="MoM or YoY — no default, refused if omitted")
    parser.add_argument("--all-series", action="store_true",
                        help="emit every ward x category series, each row still scoped "
                             "to one ward and one category (this is not aggregation)")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    # Enforcement: the null report is printed on every run, not only when asked.
    print(f"Loaded {args.input}")
    print(f"  rows       : {len(dataset['rows'])}")
    print(f"  wards      : {len(dataset['wards'])}")
    print(f"  categories : {len(dataset['categories'])}")
    print(f"  periods    : {len(dataset['periods'])} "
          f"({dataset['periods'][0]} to {dataset['periods'][-1]})")
    print(f"  NULL actual_spend rows : {dataset['null_count']}")
    for null in dataset["nulls"]:
        print(f"    {null['period']} · {null['ward']} · {null['category']}")
        print(f"        budgeted {null['budgeted_amount']:.1f}, actual MISSING — "
              f"{null['note']}")
    print()

    # Enforcement: refuse a guessed formula before doing anything else.
    if args.growth_type is None:
        sys.exit(
            "REFUSED: --growth-type was not specified.\n"
            "         MoM and YoY are different claims about the same numbers and this\n"
            "         tool will not choose for you. Pass --growth-type MoM or "
            "--growth-type YoY."
        )

    if args.all_series:
        rows = []
        for ward in dataset["wards"]:
            for category in dataset["categories"]:
                if any(r["ward"] == ward and r["category"] == category
                       for r in dataset["rows"]):
                    rows.append({"ward": ward, "category": category,
                                 "_series": compute_growth(dataset, ward, category,
                                                           args.growth_type)})
        table = [r for group in rows for r in group["_series"]]
        scope = f"{len(rows)} ward x category series"
    else:
        _refuse_aggregation(args, dataset)
        table = compute_growth(dataset, args.ward, args.category, args.growth_type)
        scope = f"{args.ward} · {args.category}"

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)

    counts = {}
    for row in table:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    print(f"Wrote {args.output}")
    print(f"  scope        : {scope}")
    print(f"  growth type  : {args.growth_type}")
    print(f"  rows written : {len(table)}")
    for status in sorted(counts):
        print(f"    {status:<21} {counts[status]}")
    flagged = [r for r in table if r["status"] in ("NULL_ACTUAL", "NULL_BASE")]
    if flagged:
        print("  flagged rows (present in output, growth deliberately not computed):")
        for row in flagged:
            print(f"    {row['period']} · {row['ward']} · {row['category']} "
                  f"· {row['status']}")


if __name__ == "__main__":
    main()

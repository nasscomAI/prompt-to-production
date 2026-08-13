"""
UC-0C — Number That Looks Right
Implementation guided by agents.md (RICE) and skills.md, per the CRAFT workflow.

Enforcement rules implemented (see agents.md):
  R1  Never aggregate across wards or categories unless explicitly instructed —
      sentinel values (ALL / * / total / ...) are refused with a clear message.
  R2  Flag every null row before computing — the null reason from the notes column
      is reported; a null actual_spend is never treated as 0 and never skipped silently.
  R3  Show the formula used in every output row alongside the result.
  R4  If --growth-type is not specified, refuse and ask — never guess MoM vs YoY
      (argparse makes --growth-type mandatory and restricts it to MoM | YoY).

Skills implemented (see skills.md):
  load_dataset   — reads CSV, validates columns, reports null count and which rows
  compute_growth — ward + category + growth_type -> per-period table with formula shown
"""
import argparse
import csv
import sys

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

AGGREGATION_SENTINELS = {"all", "*", "any", "every", "total", "combined", "grand", "overall"}

GROWTH_FORMULAS = {
    "MoM": "MoM = (current month actual_spend - previous month actual_spend) / previous month actual_spend * 100",
    "YoY": "YoY = (current actual_spend - same month previous year actual_spend) / same month previous year actual_spend * 100",
}

OUTPUT_FIELDS = [
    "period", "ward", "category", "actual_spend", "previous_actual_spend",
    "growth_pct", "formula", "flag", "flag_reason",
]


def load_dataset(input_path: str) -> dict:
    """
    Read CSV, validate columns, report null count and which rows before returning.
    Skills contract: raises a clear error if required columns are missing;
    null actual_spend rows are always reported in null_rows, never dropped.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"Input file {input_path} is empty (no header row)")
            fieldnames = reader.fieldnames
            rows = list(reader)
    except OSError as exc:
        raise FileNotFoundError(f"Cannot read input file {input_path}: {exc}") from exc

    missing = [c for c in EXPECTED_COLUMNS if c not in fieldnames]
    if missing:
        raise ValueError(
            f"Input file {input_path} is missing required column(s): {', '.join(missing)}. "
            f"Expected: {', '.join(EXPECTED_COLUMNS)}"
        )

    null_rows = []
    for row in rows:
        if not str(row.get("actual_spend", "")).strip():
            null_rows.append({
                "period": row.get("period", "?"),
                "ward": row.get("ward", "?"),
                "category": row.get("category", "?"),
                "notes": row.get("notes", "").strip() or "no reason given",
            })

    return {"fieldnames": fieldnames, "rows": rows, "null_rows": null_rows}


def _prev_month(period: str) -> str:
    year, month = int(period[:4]), int(period[5:7])
    month -= 1
    if month == 0:
        month, year = 12, year - 1
    return f"{year:04d}-{month:02d}"


def _prev_year(period: str) -> str:
    return f"{int(period[:4]) - 1:04d}{period[4:]}"


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str):
    """
    ward + category + growth_type -> per-period table with formula shown, nulls flagged.
    Returns: (output_rows, audit)
    """
    # R1 — refuse aggregation: a single ward + single category is the only allowed scope
    if not ward.strip() or ward.strip().lower() in AGGREGATION_SENTINELS:
        raise ValueError(
            "Aggregation refused: a single --ward is required. "
            f"'{ward}' looks like an all-ward request, which is not allowed."
        )
    if not category.strip() or category.strip().lower() in AGGREGATION_SENTINELS:
        raise ValueError(
            "Aggregation refused: a single --category is required. "
            f"'{category}' looks like an all-category request, which is not allowed."
        )

    # R4 — growth type explicit (also enforced by argparse choices)
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Refused: --growth-type must be MoM or YoY, got '{growth_type}' — never guessed.")

    wards = sorted({r["ward"] for r in dataset["rows"]})
    categories = sorted({r["category"] for r in dataset["rows"]})
    if ward not in wards:
        raise ValueError(f"Ward '{ward}' not found in dataset. Available wards: {', '.join(wards)}")
    if category not in categories:
        raise ValueError(f"Category '{category}' not found in dataset. Available categories: {', '.join(categories)}")

    filtered = [r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    actual_by_period = {}
    null_reasons = {}
    for row in filtered:
        p = row["period"]
        raw = str(row.get("actual_spend", "")).strip()
        if raw:
            actual_by_period[p] = float(raw)
        else:
            null_reasons[p] = row.get("notes", "").strip() or "no reason given"

    periods = sorted(set(actual_by_period) | set(null_reasons))
    formula = GROWTH_FORMULAS[growth_type]
    output_rows = []
    flag_counts = {}

    for period in periods:
        actual = actual_by_period.get(period)
        out = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual:.1f}" if actual is not None else "NULL",
            "previous_actual_spend": "",
            "growth_pct": "",
            "formula": formula,
            "flag": "",
            "flag_reason": "",
        }
        if actual is None:
            # R2 — null row: flag with the documented reason, never compute, never zero-fill
            out["flag"] = "NULL"
            out["flag_reason"] = f"actual_spend missing — {null_reasons[period]}"
            flag_counts["NULL"] = flag_counts.get("NULL", 0) + 1
        else:
            prev_period = _prev_month(period) if growth_type == "MoM" else _prev_year(period)
            prev = actual_by_period.get(prev_period)
            if prev_period in null_reasons:
                out["flag"] = "SKIPPED"
                out["flag_reason"] = f"previous period {prev_period} has null actual_spend — growth cannot be computed"
                flag_counts["SKIPPED"] = flag_counts.get("SKIPPED", 0) + 1
            elif prev is None:
                out["flag"] = "NO_DATA"
                out["flag_reason"] = f"no actual_spend for previous period {prev_period} (outside dataset)"
                flag_counts["NO_DATA"] = flag_counts.get("NO_DATA", 0) + 1
            elif prev == 0:
                out["flag"] = "SKIPPED"
                out["flag_reason"] = "previous actual_spend is 0 — growth undefined (division by zero)"
                flag_counts["SKIPPED"] = flag_counts.get("SKIPPED", 0) + 1
            else:
                growth = (actual - prev) / prev * 100
                out["previous_actual_spend"] = f"{prev:.1f}"
                out["growth_pct"] = f"{growth:+.1f}%"
        output_rows.append(out)

    audit = {"flag_counts": flag_counts, "periods": periods}
    return output_rows, audit


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name (all-ward aggregation is refused)")
    parser.add_argument("--category", required=True, help="Single category (all-category aggregation is refused)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type — must be explicit; never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        nulls = dataset["null_rows"]
        print(f"Dataset loaded: {len(dataset['rows'])} rows | {len(nulls)} null actual_spend row(s):")
        for n in nulls:
            print(f"  {n['period']} | {n['ward']} | {n['category']} | notes: {n['notes']}")

        rows, audit = compute_growth(dataset, args.ward, args.category, args.growth_type)
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows -> {args.output}")
        print(f"  scope: {args.ward} | {args.category} | {args.growth_type}")
        print(f"  flag summary: {audit['flag_counts'] or 'none'}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

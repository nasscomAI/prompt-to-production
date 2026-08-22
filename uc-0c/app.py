"""
UC-0C app.py — Number That Looks Right
Deterministic growth calculator implementing the RICE enforcement in agents.md
and the skill contracts in skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = ["MoM", "YoY"]
OUTPUT_HEADER = ["period", "ward", "category", "current_spend", "base_spend", "growth_pct", "formula", "flag"]


def load_dataset(input_path: str) -> dict:
    """
    Read the budget CSV, validate columns and values, report null actual_spend
    rows before returning.

    Returns: {"rows": [...], "null_report": {"count": int, "rows": [...]}}
    (skills.md contract).
    """
    try:
        input_file = open(input_path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"Error: cannot read input file '{input_path}': {exc}")
        sys.exit(1)

    with input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            print(f"Error: input file is missing required column(s): {missing}")
            print(f"  Found columns:    {fieldnames}")
            print(f"  Expected columns: {REQUIRED_COLUMNS}")
            sys.exit(1)

        rows = []
        null_rows = []
        bad_rows = []
        for line_no, row in enumerate(reader, start=2):
            notes = (row.get("notes") or "").strip()
            try:
                budgeted = float((row.get("budgeted_amount") or "").strip())
            except ValueError:
                bad_rows.append((line_no, f"non-numeric budgeted_amount '{row.get('budgeted_amount')}'"))
                continue

            raw_actual = (row.get("actual_spend") or "").strip()
            if raw_actual == "":
                actual = None
                null_rows.append({
                    "period": row["period"].strip(),
                    "ward": row["ward"].strip(),
                    "category": row["category"].strip(),
                    "reason": notes,
                })
            else:
                try:
                    actual = float(raw_actual)
                except ValueError:
                    bad_rows.append((line_no, f"non-numeric actual_spend '{raw_actual}'"))
                    continue

            rows.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": notes,
                "actual_raw": raw_actual,
            })

    if bad_rows:
        for line_no, problem in bad_rows:
            print(f"Error: line {line_no}: {problem} — failing validation.")
        sys.exit(1)

    return {"rows": rows, "null_report": {"count": len(null_rows), "rows": null_rows}}


def _requests_aggregation(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in {"", "all", "*", "any", "total", "combined"} or "," in v


def _refuse(message: str):
    print(f"Refusing to proceed: {message}")
    sys.exit(2)


def _parse_period(period: str):
    year, month = period.split("-")
    return int(year), int(month)


def _base_period(period: str, growth_type: str) -> str:
    year, month = _parse_period(period)
    if growth_type == "YoY":
        return f"{year - 1}-{month:02d}"
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"


def _validate_slice_args(dataset: dict, ward: str, category: str):
    if _requests_aggregation(ward) or _requests_aggregation(category):
        _refuse(
            "aggregation across wards/categories is not supported. "
            "This tool computes figures for ONE ward + ONE category per run — "
            "name them explicitly."
        )
    wards = sorted({r["ward"] for r in dataset["rows"]})
    categories = sorted({r["category"] for r in dataset["rows"]})
    if ward not in wards:
        _refuse(f"ward '{ward}' not found. Valid wards:\n  " + "\n  ".join(wards))
    if category not in categories:
        _refuse(f"category '{category}' not found. Valid categories:\n  " + "\n  ".join(categories))


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str, output_path: str):
    """
    Compute per-period spend growth for one ward + one category, writing
    growth_output.csv with the formula shown on every computed row
    (skills.md contract). Refusals exit before any output is written.
    """
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        _refuse(
            f"growth type '{growth_type}' is not supported. "
            f"Please specify --growth-type as one of: {', '.join(SUPPORTED_GROWTH_TYPES)}. "
            "Never guessing a default."
        )

    _validate_slice_args(dataset, ward, category)

    slice_rows = sorted(
        (r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category),
        key=lambda r: _parse_period(r["period"]),
    )
    by_period = {r["period"]: r for r in slice_rows}
    null_reasons = {
        (n["period"], n["ward"], n["category"]): n["reason"]
        for n in dataset["null_report"]["rows"]
    }

    out_rows = []
    flagged = 0
    computed = 0
    for row in slice_rows:
        period = row["period"]
        current = row["actual_spend"]
        flag = ""

        if current is None:
            reason = null_reasons.get((period, ward, category)) or "no reason given in notes"
            out_rows.append([period, ward, category, "", "", "", "", f"NOT_COMPUTED: {reason}"])
            flagged += 1
            continue

        base_period = _base_period(period, growth_type)
        base_row = by_period.get(base_period)

        if base_row is None:
            label = "prior-year period" if growth_type == "YoY" else "prior month"
            out_rows.append([
                period, ward, category, row["actual_raw"], "", "", "",
                f"NOT_COMPUTED: no {label} ({base_period}) present in dataset",
            ])
            flagged += 1
            continue

        if base_row["actual_spend"] is None:
            reason = null_reasons.get((base_period, ward, category)) or "no reason given in notes"
            out_rows.append([
                period, ward, category, row["actual_raw"], "", "", "",
                f"NOT_COMPUTED: comparison base {base_period} is null ({reason})",
            ])
            flagged += 1
            continue

        pct = (current - base_row["actual_spend"]) / base_row["actual_spend"] * 100
        growth_str = f"{pct:+.1f}%"
        formula = (
            f"({row['actual_raw']} - {base_row['actual_raw']}) "
            f"/ {base_row['actual_raw']} * 100 = {growth_str}"
        )
        out_rows.append([
            period,
            ward,
            category,
            row["actual_raw"],
            base_row["actual_raw"],
            growth_str,
            formula,
            flag,
        ])
        computed += 1

    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(OUTPUT_HEADER)
        writer.writerows(out_rows)

    print(
        f"Done. Wrote {len(out_rows)} periods for '{ward}' / '{category}' ({growth_type}): "
        f"{computed} computed, {flagged} flagged NOT_COMPUTED. "
        f"Null rows reported at load: {dataset['null_report']['count']}. "
        f"Output written to {output_path}"
    )


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help='Exact ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=True, help='Exact category name, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="Required: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    print(f'Loaded {len(dataset["rows"])} rows. Null report BEFORE computing:')
    for n in dataset["null_report"]["rows"]:
        print(f'  - {n["period"]} | {n["ward"]} | {n["category"]} | reason: "{n["reason"]}"')

    compute_growth(dataset, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()

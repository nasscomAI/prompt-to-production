"""
UC-0C — Number That Looks Right
Per-ward per-category growth calculator with refusal and null-flagging rules.

RICE enforcement (see agents.md):
1. Never aggregate across wards/categories — refuse "all wards" requests.
2. Flag every null actual_spend row (quote the notes reason), never skip.
3. Show the formula in every output row.
4. Refuse if --growth-type is missing or invalid — never guess.
5. Growth uses actual_spend only; first period of series is N/A.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str):
    """Read CSV, validate columns, report null rows before returning."""
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print(f"ERROR: cannot read dataset {path}: {exc}", file=sys.stderr)
        raise SystemExit(1)

    with fh as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            print(f"ERROR: dataset is missing required column(s): {missing}",
                  file=sys.stderr)
            raise SystemExit(1)
        rows = list(reader)

    null_report = []
    for row in rows:
        spend = (row.get("actual_spend") or "").strip()
        if spend == "":
            null_report.append(row)
    print(f"Loaded {len(rows)} rows — {len(null_report)} null actual_spend rows:")
    for row in null_report:
        print(f"  NULL: {row['period']} | {row['ward']} | {row['category']} "
              f"| reason from notes: {(row.get('notes') or '').strip() or '(no note)'}")
    return rows, null_report


def _refuse(msg: str):
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def compute_growth(rows, ward: str, category: str, growth_type: str, output_path: str):
    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    series.sort(key=lambda r: r["period"])
    if not series:
        wards = sorted({r["ward"] for r in rows})
        cats = sorted({r["category"] for r in rows})
        _refuse(f"no rows for ward '{ward}' / category '{category}'. "
                f"Valid wards: {wards}; valid categories: {cats}")

    step = 1 if growth_type == "MoM" else 12
    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_pct", "formula", "flag", "notes"]
    out_rows = []
    prev_spend = None
    prev_period = None
    for row in series:
        spend_raw = (row["actual_spend"] or "").strip()
        note = (row.get("notes") or "").strip()
        if spend_raw == "":
            out_rows.append({
                "period": row["period"], "ward": ward, "category": category,
                "actual_spend": "NULL", "growth_pct": "NOT_COMPUTED",
                "formula": "not computed — actual_spend is NULL",
                "flag": "NULL_SPEND_NOT_COMPUTED", "notes": note,
            })
            prev_spend, prev_period = None, row["period"]
            continue
        spend = float(spend_raw)
        if prev_spend is None:
            growth = "N/A (no prior period)"
            formula = "n/a — first period of series"
            flag = ""
        else:
            pct = (spend - prev_spend) / prev_spend * 100.0
            growth = f"{pct:+.1f}%"
            formula = (f"({spend:g} \u2212 {prev_spend:g}) \u00f7 {prev_spend:g} "
                       f"\u00d7 100 = {growth} ({growth_type} vs {prev_period})")
            flag = ""
        out_rows.append({
            "period": row["period"], "ward": ward, "category": category,
            "actual_spend": f"{spend:g}", "growth_pct": growth,
            "formula": formula, "flag": flag, "notes": note,
        })
        prev_spend, prev_period = spend, row["period"]

    # Dataset-wide null rows are appended, flagged, never skipped (rule 2).
    for row in rows:
        if (row["actual_spend"] or "").strip() == "" and not (
                row["ward"] == ward and row["category"] == category):
            out_rows.append({
                "period": row["period"], "ward": row["ward"],
                "category": row["category"], "actual_spend": "NULL",
                "growth_pct": "NOT_COMPUTED",
                "formula": "not computed — actual_spend is NULL",
                "flag": "NULL_SPEND_NOT_COMPUTED",
                "notes": (row.get("notes") or "").strip(),
            })

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {len(series)} series rows + dataset-wide null flags "
          f"to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY — required, the tool refuses to guess")
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()

    if not args.ward or args.ward.strip().lower() in {"all", "*", "any"}:
        _refuse("all-ward aggregation is not permitted — specify exactly one ward. "
                "Cross-ward totals hide per-ward variance and null rows.")
    if not args.category or args.category.strip().lower() in {"all", "*", "any"}:
        _refuse("all-category aggregation is not permitted — specify exactly one category.")
    if args.growth_type is None:
        _refuse("growth type not specified — pass --growth-type MoM or YoY. "
                "The formula will not be guessed silently.")
    if args.growth_type not in ("MoM", "YoY"):
        _refuse(f"unknown growth type '{args.growth_type}' — only MoM and YoY are supported.")

    rows, _ = load_dataset(args.input)
    compute_growth(rows, args.ward.strip(), args.category.strip(),
                   args.growth_type, args.output)


if __name__ == "__main__":
    main()

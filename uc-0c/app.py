"""
UC-0C app.py — Budget Growth Analyzer ("Number That Looks Right").

Computes MoM or YoY spend growth for exactly ONE ward and ONE category. It
refuses to aggregate, refuses to guess the growth-type, flags every null
actual_spend row with its reason, and shows the formula on every computed row.

Run:
  python app.py --input ../data/budget/ward_budget.csv \
                --ward "Ward 1 - Kasba" \
                --category "Roads & Pothole Repair" \
                --growth-type MoM \
                --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
AGGREGATE_TOKENS = {"all", "*", "total", "aggregate", "everything", "combined"}
OUTPUT_FIELDS = [
    "period", "ward", "category", "actual_spend",
    "comparison_period", "comparison_spend", "growth_type", "growth_percent", "formula", "note",
]


def _norm(value: str) -> str:
    """Normalize for matching: unify dash variants, collapse spaces, lowercase.
    Lets a CLI hyphen match the dataset's en-dash ward names."""
    if value is None:
        return ""
    v = value.replace("–", "-").replace("—", "-")
    return " ".join(v.split()).strip().lower()


def _parse_spend(raw: str):
    if raw is None or str(raw).strip() == "":
        return None
    return float(raw)


def load_dataset(path: str) -> tuple:
    """Read the budget CSV, validate columns, and report nulls before returning.

    Returns: (rows, null_rows). Raises ValueError if required columns are missing.
    """
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Dataset missing required columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if _parse_spend(r.get("actual_spend")) is None]
    print(f"load_dataset: {len(rows)} rows read. Null actual_spend rows: {len(null_rows)}")
    for r in null_rows:
        reason = (r.get("notes") or "").strip() or "(no reason given)"
        print(f"  NULL -> {r['period']} | {r['ward']} | {r['category']} | reason: {reason}")
    return rows, null_rows


def _comparison_period(period: str, growth_type: str):
    year, month = period.split("-")
    if growth_type == "MoM":
        m = int(month) - 1
        if m >= 1:
            return f"{year}-{m:02d}"
        return f"{int(year) - 1}-12"
    # YoY
    return f"{int(year) - 1}-{month}"


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Return a per-period growth table for one ward + one category.

    Each entry is a dict matching OUTPUT_FIELDS. Null rows and null-gap rows are
    flagged, never computed. Formula is shown on every computed row.
    """
    subset = [
        r for r in rows
        if _norm(r.get("ward")) == _norm(ward) and _norm(r.get("category")) == _norm(category)
    ]
    if not subset:
        return []

    spend_by_period = {r["period"]: _parse_spend(r.get("actual_spend")) for r in subset}
    notes_by_period = {r["period"]: (r.get("notes") or "").strip() for r in subset}
    ward_label = subset[0]["ward"]
    category_label = subset[0]["category"]

    table = []
    for period in sorted(spend_by_period):
        curr = spend_by_period[period]
        comp_period = _comparison_period(period, growth_type)
        prev = spend_by_period.get(comp_period)

        entry = {
            "period": period,
            "ward": ward_label,
            "category": category_label,
            "actual_spend": "" if curr is None else curr,
            "comparison_period": comp_period,
            "comparison_spend": "" if prev is None else prev,
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": "",
            "note": "",
        }

        if curr is None:
            entry["growth_percent"] = "NOT COMPUTED"
            entry["note"] = f"NULL actual_spend: {notes_by_period.get(period) or '(no reason given)'}"
        elif comp_period not in spend_by_period:
            entry["growth_percent"] = "N/A"
            entry["note"] = f"No comparison period ({comp_period}) in dataset"
        elif prev is None:
            entry["growth_percent"] = "NOT COMPUTED"
            entry["note"] = f"Comparison period {comp_period} is NULL: {notes_by_period.get(comp_period) or '(no reason given)'}"
        else:
            growth = (curr - prev) / prev * 100
            entry["growth_percent"] = round(growth, 1)
            entry["formula"] = f"{growth_type} = ({curr} - {prev}) / {prev} * 100"

        table.append(entry)

    return table


def _refuse(message: str) -> None:
    print(f"REFUSED: {message}")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Exactly one ward")
    parser.add_argument("--category", default=None, help="Exactly one category")
    parser.add_argument("--growth-type", dest="growth_type", default=None, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    # Enforcement rule 4: never guess the growth-type.
    if not args.growth_type:
        _refuse("growth-type not specified. Please pass --growth-type MoM or --growth-type YoY. "
                "I will not guess which one you meant.")
    if args.growth_type not in ("MoM", "YoY"):
        _refuse(f"growth-type '{args.growth_type}' is invalid. Use MoM or YoY.")

    # Enforcement rule 1: never aggregate — a single ward and category are required.
    if not args.ward or _norm(args.ward) in AGGREGATE_TOKENS:
        _refuse("no single ward specified. This tool never aggregates across wards. "
                "Pass exactly one --ward.")
    if not args.category or _norm(args.category) in AGGREGATE_TOKENS:
        _refuse("no single category specified. This tool never aggregates across categories. "
                "Pass exactly one --category.")

    rows, _ = load_dataset(args.input)  # rule 2: nulls reported here, before compute
    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    if not table:
        _refuse(f"no rows found for ward '{args.ward}' and category '{args.category}'. "
                "Check the exact ward/category spelling.")

    with open(args.output, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)

    computed = sum(1 for e in table if isinstance(e["growth_percent"], (int, float)))
    flagged = sum(1 for e in table if e["growth_percent"] in ("NOT COMPUTED", "N/A"))
    print(f"Done. Growth table written to {args.output}")
    print(f"Ward: {table[0]['ward']} | Category: {table[0]['category']} | Type: {args.growth_type}")
    print(f"Periods: {len(table)} | Computed: {computed} | Flagged/not computed: {flagged}")


if __name__ == "__main__":
    main()

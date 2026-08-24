"""
UC-0C — Number That Looks Right
Implements the enforcement rules from agents.md:
- never aggregate across wards or categories unless explicitly instructed — refuse if asked
- flag every null actual_spend row before computing, reporting the reason from notes
- show the formula used in every output row alongside the result
- refusal condition: if --growth-type is not specified, refuse and ask, never guess
"""
import argparse
import csv


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(input_path: str) -> list:
    """Read the CSV, validate columns, and report null rows before computing."""
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Input CSV is missing required columns: {', '.join(missing)}")
        rows = list(reader)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print(f"Dataset loaded: {len(rows)} rows, {len(null_rows)} null actual_spend rows.")
    for r in null_rows:
        print(f"  NULL: {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes']}")
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str, output_path: str) -> None:
    """Compute a per-period growth table for one ward + one category, flagging nulls."""
    scoped = [r for r in rows if r["ward"] == ward and r["category"] == category]
    scoped.sort(key=lambda r: r["period"])

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "period", "ward", "category", "actual_spend", "previous_period_value",
            "growth_pct", "formula", "status", "notes"])
        writer.writeheader()

        for r in null_rows:
            writer.writerow({
                "period": r["period"], "ward": r["ward"], "category": r["category"],
                "actual_spend": "", "previous_period_value": "",
                "growth_pct": "", "formula": "not computed - null actual_spend",
                "status": "FLAGGED_NULL", "notes": r["notes"]})

        if not scoped:
            print(f"WARNING: no rows found for ward '{ward}' and category '{category}'.")
            return

        if growth_type == "MoM":
            previous_value = None
            for r in scoped:
                if not (r.get("actual_spend") or "").strip():
                    continue
                current = float(r["actual_spend"])
                if previous_value is None or previous_value == 0:
                    growth_pct = ""
                    formula = f"({current} - n/a) / n/a"
                    status = "FLAGGED_NO_BASE"
                else:
                    growth_pct = round((current - previous_value) / previous_value * 100, 1)
                    formula = f"(({current} - {previous_value}) / {previous_value}) * 100"
                    status = "COMPUTED"
                writer.writerow({
                    "period": r["period"], "ward": r["ward"], "category": r["category"],
                    "actual_spend": current, "previous_period_value": "" if previous_value is None else previous_value,
                    "growth_pct": growth_pct, "formula": formula, "status": status, "notes": r["notes"]})
                previous_value = current
        else:
            raise ValueError("Only MoM growth is supported. YoY would require the prior-year dataset.")

    print(f"Growth table written to {output_path} (ward: {ward}, category: {category}, type: {growth_type}).")


def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator.")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name — one ward only")
    parser.add_argument("--category", required=True, help="Exact category — one category only")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type — REQUIRED, never guessed")
    parser.add_argument("--output", required=True, help="Path for growth_output.csv")
    args = parser.parse_args()

    if args.ward.strip().lower() in ("all", "every ward", "total", "any"):
        raise SystemExit("REFUSED: aggregation across wards is not permitted. Specify exactly one ward.")
    if args.category.strip().lower() in ("all", "all categories", "total", "any"):
        raise SystemExit("REFUSED: aggregation across categories is not permitted. Specify exactly one category.")

    rows = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)


if __name__ == "__main__":
    main()

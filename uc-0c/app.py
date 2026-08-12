"""
UC-0C — Number That Looks Right.
Per-ward per-category budget growth calculator implementing load_dataset +
compute_growth per skills.md, enforced per agents.md (no aggregation,
null flagging, formula shown, growth-type never guessed).
"""
import argparse
import csv

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")


def _parse_amount(value: str):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_dataset(input_path: str) -> dict:
    """Reads the budget CSV, validates columns, reports null rows with notes."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    if not rows:
        raise ValueError(f"Input CSV has no data rows: {input_path}")

    missing = [c for c in EXPECTED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(
            f"Input CSV missing expected columns: {missing}. "
            f"Expected: {EXPECTED_COLUMNS}"
        )

    null_rows = []
    for row in rows:
        if _parse_amount(row.get("actual_spend")) is None:
            null_rows.append({
                "period": row.get("period", ""),
                "ward": row.get("ward", ""),
                "category": row.get("category", ""),
                "notes": (row.get("notes") or "").strip() or "No reason given",
            })

    if null_rows:
        print(f"NULL REPORT: {len(null_rows)} row(s) with missing actual_spend:")
        for n in null_rows:
            print(f"  {n['period']} · {n['ward']} · {n['category']} — {n['notes']}")
    else:
        print("NULL REPORT: 0 rows with missing actual_spend")

    return {"rows": rows, "null_rows": null_rows}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """Computes per-period growth for one ward + category scope, formula shown."""
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Refusing to compute: --growth-type '{growth_type}' is not supported. "
            f"Specify MoM or YoY — never guessed."
        )

    rows = dataset["rows"]
    wards = {r["ward"] for r in rows}
    categories = {r["category"] for r in rows}

    if ward not in wards:
        raise ValueError(
            f"Refusing to aggregate or guess: ward '{ward}' not in dataset. "
            f"Available wards: {sorted(wards)}"
        )
    if category not in categories:
        raise ValueError(
            f"Refusing to aggregate or guess: category '{category}' not in dataset. "
            f"Available categories: {sorted(categories)}"
        )

    scoped = [r for r in rows if r["ward"] == ward and r["category"] == category]
    scoped.sort(key=lambda r: r["period"])

    results = []
    for index, row in enumerate(scoped):
        current = _parse_amount(row.get("actual_spend"))
        period = row.get("period", "")

        if growth_type == "MoM":
            base_row = scoped[index - 1] if index > 0 else None
        else:
            base_row = None

        base = _parse_amount(base_row["actual_spend"]) if base_row else None
        base_period = base_row["period"] if base_row else ""

        if current is None:
            growth_pct = ""
            formula = "N/A — actual_spend is NULL: not computed"
            notes = (row.get("notes") or "").strip() or "No reason given"
        elif base is None:
            growth_pct = ""
            reason = ("first period of series" if base_row is None
                      else f"base period {base_period} has NULL actual_spend")
            formula = f"N/A — no base period for {growth_type}: {reason}"
            notes = row.get("notes") or "No base period"
        else:
            growth = (current - base) / base * 100
            if growth > 0:
                growth_pct = f"+{growth:.1f}%"
            else:
                growth_pct = f"{growth:.1f}%"
            formula = (f"{growth_type} = ({current:g} − {base:g}) / {base:g} × 100, "
                       f"base {base_period} → {period}")
            notes = row.get("notes") or ""

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "" if current is None else f"{current:g}",
            "growth_pct": growth_pct,
            "formula": formula,
            "notes": notes,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (single ward only)")
    parser.add_argument("--category", required=True, help="Category name (single category only)")
    parser.add_argument("--growth-type", required=True, choices=list(VALID_GROWTH_TYPES),
                        help="MoM or YoY — must be specified explicitly")
    parser.add_argument("--output", required=True, help="Path to write growth table CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["period", "ward", "category", "actual_spend",
                        "growth_pct", "formula", "notes"],
        )
        writer.writeheader()
        writer.writerows(results)

    computed = sum(1 for r in results if r["growth_pct"])
    flagged = len(results) - computed
    print(f"Computed {computed} growth rows, flagged {flagged} as not computed -> {args.output}")
    print(f"Done. Growth table written to {args.output}")


if __name__ == "__main__":
    main()
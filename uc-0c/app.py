"""
UC-0C — Number That Looks Right
Per-ward, per-category budget growth calculator.

The failure mode here is a number that is arithmetically clean but wrong in
meaning: an all-ward total presented as if it were one ward, a null spend
silently treated as zero, or a growth type (MoM vs YoY) chosen for you without
being asked. This tool refuses each of those. It computes growth for exactly one
ward + one category, flags every null instead of computing through it, shows the
formula on every row, and refuses if the growth type is not specified.
"""
import argparse
import csv

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = {"MoM", "YoY"}
# Sentinel values that mean "give me everything" — which this tool must refuse.
AGGREGATE_TOKENS = {"all", "all wards", "all categories", "total", "*", "everything"}


def load_dataset(path: str) -> dict:
    """
    Read the budget CSV, validate columns, and report null actual_spend rows
    BEFORE any computation happens.

    Returns:
        {"rows": [<dict per row>], "nulls": [<row dict>, ...], "columns": [...]}

    Raises ValueError if a required column is missing.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in columns]
        if missing:
            raise ValueError(f"Input is missing required column(s): {missing}")
        rows = list(reader)

    nulls = [r for r in rows if (r.get("actual_spend") or "").strip() == ""]

    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(nulls)}.")
    for r in nulls:
        note = (r.get("notes") or "").strip() or "(no reason given)"
        print(f"  NULL  {r['period']} · {r['ward']} · {r['category']}  — reason: {note}")

    return {"rows": rows, "nulls": nulls, "columns": columns}


def _refuse(reason: str) -> dict:
    return {"refused": True, "reason": reason, "table": []}


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> dict:
    """
    Compute period-over-period growth for ONE ward + ONE category.

    Enforcement (mirrors agents.md):
      * Refuse if ward or category names an aggregate ("all"/"total"/etc.) —
        never blend wards or categories into a single number.
      * Refuse if growth_type is not exactly MoM or YoY — never guess.
      * Flag every null row (reason from the notes column); never compute through it.
      * Show the formula used in every computed row.

    Returns {"refused": bool, "reason": str, "table": [<row dicts>]}.
    """
    if not growth_type or growth_type not in VALID_GROWTH_TYPES:
        return _refuse(
            f"--growth-type must be specified as one of {sorted(VALID_GROWTH_TYPES)}. "
            "Refusing to guess MoM vs YoY."
        )
    if not ward or ward.strip().lower() in AGGREGATE_TOKENS:
        return _refuse(
            "Refusing to aggregate across wards. Specify exactly one ward "
            "(e.g. --ward \"Ward 1 – Kasba\")."
        )
    if not category or category.strip().lower() in AGGREGATE_TOKENS:
        return _refuse(
            "Refusing to aggregate across categories. Specify exactly one category "
            "(e.g. --category \"Roads & Pothole Repair\")."
        )

    # Filter to the single ward + category and sort by period.
    series = [r for r in dataset["rows"]
              if r["ward"] == ward and r["category"] == category]
    if not series:
        return _refuse(
            f"No rows found for ward={ward!r} and category={category!r}. "
            "Check the exact spelling (names include the ward number and en-dash)."
        )
    series.sort(key=lambda r: r["period"])

    # Index by period for previous-period lookup.
    by_period = {r["period"]: r for r in series}
    lag = 1 if growth_type == "MoM" else 12  # months back

    def parse_spend(r):
        raw = (r.get("actual_spend") or "").strip()
        return None if raw == "" else float(raw)

    def prev_period(period: str) -> str:
        y, m = (int(x) for x in period.split("-"))
        idx = (y * 12 + (m - 1)) - lag
        return f"{idx // 12:04d}-{idx % 12 + 1:02d}"

    table = []
    for r in series:
        period = r["period"]
        cur = parse_spend(r)
        prev_p = prev_period(period)
        prev_row = by_period.get(prev_p)
        prev = parse_spend(prev_row) if prev_row else None

        out = {
            "period": period,
            "ward": ward,
            "category": category,
            "growth_type": growth_type,
            "actual_spend": "" if cur is None else cur,
            "prev_period": prev_p,
            "prev_spend": "" if prev is None else prev,
            "formula": "",
            "growth_pct": "",
            "flag": "",
        }

        if cur is None:
            note = (r.get("notes") or "").strip() or "(no reason given)"
            out["flag"] = f"NULL_CURRENT — not computed (reason: {note})"
        elif prev_row is None:
            out["flag"] = f"NO_PRIOR_PERIOD ({prev_p} not in data) — not computed"
        elif prev is None:
            note = (prev_row.get("notes") or "").strip() or "(no reason given)"
            out["flag"] = f"NULL_PRIOR — {prev_p} is null (reason: {note}) — not computed"
        elif prev == 0:
            out["flag"] = "PRIOR_ZERO — growth undefined (division by zero) — not computed"
        else:
            growth = (cur - prev) / prev * 100
            out["formula"] = f"({cur} - {prev}) / {prev} x 100"
            out["growth_pct"] = round(growth, 1)

        table.append(out)

    return {"refused": False, "reason": "", "table": table}


def write_table(result: dict, output_path: str):
    fieldnames = ["period", "ward", "category", "growth_type", "actual_spend",
                  "prev_period", "prev_spend", "formula", "growth_pct", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result["table"])


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exactly one ward, e.g. \"Ward 1 – Kasba\"")
    parser.add_argument("--category", help="Exactly one category, e.g. \"Roads & Pothole Repair\"")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY — REQUIRED, never defaulted")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    result = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if result["refused"]:
        print("\nREFUSED: " + result["reason"])
        # Still write an output file documenting the refusal, so the run is auditable.
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["status", "reason"])
            writer.writerow(["REFUSED", result["reason"]])
        print(f"Refusal recorded in {args.output}")
        return

    write_table(result, args.output)
    computed = sum(1 for r in result["table"] if r["growth_pct"] != "")
    flagged = sum(1 for r in result["table"] if r["flag"] != "")
    print(f"\nComputed {computed} growth values, flagged {flagged} rows "
          f"(null / no-prior). Output written to {args.output}")


if __name__ == "__main__":
    main()

"""
UC-0C — Number That Looks Right (scoped budget-growth calculator).

Implements agents.md (RICE) + skills.md (load_dataset, compute_growth).

Compliance by construction (see agents.md E1–E4):
  E1 one ward + one category per run; multi-scope/unknown scope is refused.
  E2 nulls are reported before computing and flagged with notes reasons.
  E3 every row shows its formula (or the reason no computation applies).
  E4 missing --growth-type is refused, never guessed; YoY has no baseline.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]
OUTPUT_FIELDS = ["period", "ward", "category", "budgeted_amount",
                 "actual_spend", "growth_pct", "formula", "flag", "notes"]
MULTI_SCOPE_TOKENS = {"all", "*", "all wards", "all categories"}


def _parse_amount(raw):
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_dataset(path: str) -> dict:
    """Read the budget CSV, validate columns, report nulls, return rows."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Budget file not found: {path}")
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLUMNS
                   if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        rows = [dict(r) for r in reader]

    nulls = []
    for r in rows:
        if _parse_amount(r.get("actual_spend")) is None:
            nulls.append({"period": (r.get("period") or "").strip(),
                          "ward": (r.get("ward") or "").strip(),
                          "category": (r.get("category") or "").strip(),
                          "reason": (r.get("notes") or "").strip()
                          or "no reason given"})
    print(f"Loaded {len(rows)} rows. Null actual_spend: {len(nulls)}.")
    for n in nulls:
        print(f"  NULL: {n['period']} | {n['ward']} | {n['category']} "
              f"— {n['reason']}")
    return {"rows": rows, "null_report": nulls}


def _reject_scope(value: str, kind: str, valid: set):
    if value is None or not str(value).strip():
        raise ValueError(f"Refusing: --{kind} is required (single value).")
    v = str(value).strip()
    if v.lower() in MULTI_SCOPE_TOKENS or "," in v:
        raise ValueError(
            f"Refusing all-{kind} aggregation for {v!r}: request exactly one "
            f"{kind}.")
    if v not in valid:
        raise ValueError(
            f"Refusing: unknown {kind} {v!r}. Valid values: {sorted(valid)}.")
    return v


def compute_growth(rows: list, ward: str, category: str,
                   growth_type: str) -> list:
    """Per-period growth table for one ward + one category, formulas shown."""
    if growth_type is None or not str(growth_type).strip():
        raise ValueError("Refusing to guess: --growth-type is required "
                         "(MoM or YoY).")
    gt = str(growth_type).strip()
    if gt not in ("MoM", "YoY"):
        raise ValueError(f"Refusing: unknown --growth-type {gt!r}. "
                         f"Use MoM or YoY.")

    wards = {str(r.get("ward", "")).strip() for r in rows}
    cats = {str(r.get("category", "")).strip() for r in rows}
    ward = _reject_scope(ward, "ward", wards)
    category = _reject_scope(category, "category", cats)

    sliced = [r for r in rows
              if str(r.get("ward", "")).strip() == ward
              and str(r.get("category", "")).strip() == category]
    sliced.sort(key=lambda r: (r.get("period") or "").strip())

    table = []
    prev_actual = None
    for r in sliced:
        period = (r.get("period") or "").strip()
        budgeted = (r.get("budgeted_amount") or "").strip()
        actual_raw = (r.get("actual_spend") or "").strip()
        notes = (r.get("notes") or "").strip()
        actual = _parse_amount(actual_raw)

        if gt == "YoY":
            # No 2023 data exists — flag every row instead of inventing it.
            table.append({"period": period, "ward": ward, "category": category,
                          "budgeted_amount": budgeted,
                          "actual_spend": actual_raw, "growth_pct": "",
                          "formula": "n/a (YoY needs prior-year actuals, "
                                     "not in dataset)",
                          "flag": "NO_BASELINE", "notes": notes})
            continue

        # MoM
        if actual is None:
            reason = notes or "no reason given"
            table.append(
                {"period": period, "ward": ward, "category": category,
                 "budgeted_amount": budgeted, "actual_spend": actual_raw,
                 "growth_pct": "",
                 "formula": "n/a (actual_spend null — not computed)",
                 "flag": f"NULL_ACTUAL: {reason}", "notes": notes})
        elif prev_actual is None:
            if len(table) == 0:
                formula = "n/a (first period, no prior actual_spend)"
                flag = "FIRST_PERIOD"
            else:
                formula = ("n/a (baseline period actual_spend null — "
                           "not computed)")
                flag = "NULL_BASELINE"
            table.append({"period": period, "ward": ward, "category": category,
                          "budgeted_amount": budgeted,
                          "actual_spend": actual_raw, "growth_pct": "",
                          "formula": formula, "flag": flag, "notes": notes})
        elif prev_actual == 0:
            table.append({"period": period, "ward": ward, "category": category,
                          "budgeted_amount": budgeted,
                          "actual_spend": actual_raw, "growth_pct": "",
                          "formula": "n/a (baseline actual_spend is zero — "
                                     "not computed)",
                          "flag": "ZERO_BASELINE", "notes": notes})
        else:
            growth = (actual - prev_actual) / prev_actual * 100
            sign = "+" if growth >= 0 else "-"
            table.append(
                {"period": period, "ward": ward, "category": category,
                 "budgeted_amount": budgeted, "actual_spend": actual_raw,
                 "growth_pct": f"{sign}{abs(growth):.1f}%",
                 "formula": f"MoM: ({actual}-{prev_actual})/{prev_actual}*100",
                 "flag": "", "notes": notes})
        if actual is not None:
            prev_actual = actual
        else:
            prev_actual = None  # null breaks the chain — never carry over

    return table


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="UC-0C scoped budget-growth calculator")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None,
                        help="Exactly one ward (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, default=None,
                        help="Exactly one category")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="MoM or YoY (required — never guessed)")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args(argv)

    try:
        dataset = load_dataset(args.input)
        table = compute_growth(dataset["rows"], args.ward, args.category,
                               args.growth_type)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Refused: {exc}", file=sys.stderr)
        sys.exit(2)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)
    print(f"Done. {args.growth_type} growth for {args.ward} | "
          f"{args.category}: {len(table)} periods written to {args.output}")


if __name__ == "__main__":
    main()

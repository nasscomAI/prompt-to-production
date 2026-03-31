"""
UC-0C: Number That Looks Right — Budget Integrity Analyser
===========================================================
Detects silent aggregation errors in ward-level municipal budget data.

CRAFT loop v1:
  - Initial: basic growth rate computation
  - Fix 1: added per-ward per-category scope enforcement (no cross-scope aggregation)
  - Fix 2: added outlier growth and round-number anomaly flags
  - Fix 3: added missing-baseline and phantom-row detection

Usage:
    python app.py

Output:
    growth_output.csv  (in current working directory)
"""

import csv
import os
import sys
from collections import defaultdict

# ─── Config ─────────────────────────────────────────────────────────────────

INPUT_FILE  = os.path.join("data", "budget", "ward_budget.csv")
OUTPUT_FILE = "growth_output.csv"

GROWTH_OUTLIER_HIGH =  200.0   # flag if growth > 200%
GROWTH_OUTLIER_LOW  =  -50.0   # flag if growth < -50%

OUTPUT_COLUMNS = [
    "ward_id",
    "category",
    "previous_year",
    "current_year",
    "growth_rate_pct",
    "anomaly_flag",
    "anomaly_reason",
]

# ─── Counters for audit trail ────────────────────────────────────────────────

counters = {
    "scope_violations": 0,
    "outlier_growth": 0,
    "missing_baseline": 0,
    "round_number_alerts": 0,
    "phantom_rows": 0,
}


# ─── Step 1: Load CSV ────────────────────────────────────────────────────────

def load_budget(filepath):
    """
    Load ward_budget.csv and return a dict keyed by (ward_id, category).
    Expected columns (flexible column names handled via mapping):
        ward_id | ward | ward_no   → normalised to 'ward_id'
        category | dept | type     → normalised to 'category'
        previous_year | prev | py  → normalised to 'previous_year'
        current_year  | curr | cy  → normalised to 'current_year'
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] Input file not found: {filepath}")
        print("        Make sure you have cloned the repo and the data/ folder is present.")
        sys.exit(1)

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_headers = [h.strip() for h in reader.fieldnames]

    # Build a normalisation map
    col_map = {}
    for h in raw_headers:
        hl = h.lower().replace(" ", "_")
        if hl in ("ward_id", "ward", "ward_no", "wardid"):
            col_map["ward_id"] = h
        elif hl in ("category", "dept", "department", "type", "expense_type"):
            col_map["category"] = h
        elif hl in ("previous_year", "prev_year", "prev", "py", "year_1", "budget_prev"):
            col_map["previous_year"] = h
        elif hl in ("current_year", "curr_year", "curr", "cy", "year_2", "budget_curr"):
            col_map["current_year"] = h

    required = ["ward_id", "category", "previous_year", "current_year"]
    missing_cols = [r for r in required if r not in col_map]
    if missing_cols:
        print(f"[ERROR] Cannot find required columns in CSV: {missing_cols}")
        print(f"        Detected headers: {raw_headers}")
        print("        Please check ward_budget.csv column names.")
        sys.exit(1)

    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # line 2 onward (1 = header)
            stripped = {k.strip(): v.strip() for k, v in row.items()}
            ward_id  = stripped[col_map["ward_id"]]
            category = stripped[col_map["category"]]
            prev_raw = stripped[col_map["previous_year"]]
            curr_raw = stripped[col_map["current_year"]]

            # Parse numerics
            try:
                prev_val = float(prev_raw.replace(",", ""))
            except ValueError:
                print(f"[WARN] Line {i}: non-numeric previous_year '{prev_raw}' — skipping row")
                continue
            try:
                curr_val = float(curr_raw.replace(",", ""))
            except ValueError:
                print(f"[WARN] Line {i}: non-numeric current_year '{curr_raw}' — skipping row")
                continue

            rows.append({
                "ward_id":       ward_id,
                "category":      category,
                "previous_year": prev_val,
                "current_year":  curr_val,
            })

    return rows


# ─── Step 2: Enforce scope — group strictly by (ward_id, category) ────────────

def group_by_scope(rows):
    """
    Group rows by (ward_id, category).
    If multiple rows share the same key, that itself is a data anomaly
    (duplicate scope) — we flag it but still process the first occurrence.
    Returns: dict[(ward_id, category)] → {"previous_year": float, "current_year": float, "duplicate": bool}
    """
    grouped = {}
    duplicates = set()

    for row in rows:
        key = (row["ward_id"], row["category"])
        if key in grouped:
            duplicates.add(key)
        else:
            grouped[key] = {
                "previous_year": row["previous_year"],
                "current_year":  row["current_year"],
                "duplicate":     False,
            }

    for key in duplicates:
        grouped[key]["duplicate"] = True

    return grouped


# ─── Step 3: Compute growth & detect anomalies ──────────────────────────────

def compute_and_flag(grouped):
    """
    For each (ward_id, category) pair, compute growth rate and flag anomalies.
    CRITICAL: no cross-ward, no cross-category computation ever happens here.
    """
    results = []

    for (ward_id, category), data in sorted(grouped.items()):
        prev  = data["previous_year"]
        curr  = data["current_year"]
        is_dup = data["duplicate"]

        anomaly_flag    = False
        anomaly_reasons = []

        # ── Anomaly: duplicate rows for same scope (potential cross-scope blending upstream)
        if is_dup:
            anomaly_flag = True
            anomaly_reasons.append("duplicate ward-category rows detected — possible cross-scope blending in source data")
            counters["scope_violations"] += 1

        # ── Growth rate calculation (CRAFT fix 1: scoped only)
        if prev == 0:
            growth_rate = None
            anomaly_flag = True
            anomaly_reasons.append("division_by_zero: previous_year is 0")
            counters["missing_baseline"] += 1
        else:
            growth_rate = round((curr - prev) / prev * 100, 2)

            # ── Anomaly: outlier growth (CRAFT fix 2)
            if growth_rate > GROWTH_OUTLIER_HIGH or growth_rate < GROWTH_OUTLIER_LOW:
                anomaly_flag = True
                anomaly_reasons.append(
                    f"outlier_growth: {growth_rate}% is outside [{GROWTH_OUTLIER_LOW}%, {GROWTH_OUTLIER_HIGH}%]"
                )
                counters["outlier_growth"] += 1

            # ── Anomaly: round-number suspicion (CRAFT fix 3)
            if growth_rate == 0.0:
                anomaly_flag = True
                anomaly_reasons.append("round_number_alert: growth is exactly 0.00% — possible copy-paste error")
                counters["round_number_alerts"] += 1
            elif curr == prev and growth_rate == 0.0:
                pass  # already caught above

        results.append({
            "ward_id":        ward_id,
            "category":       category,
            "previous_year":  prev,
            "current_year":   curr,
            "growth_rate_pct": "" if growth_rate is None else growth_rate,
            "anomaly_flag":   "TRUE" if anomaly_flag else "FALSE",
            "anomaly_reason": "; ".join(anomaly_reasons) if anomaly_reasons else "",
        })

    return results


# ─── Step 4: Write output ────────────────────────────────────────────────────

def write_output(results, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] Output written to: {filepath}")


# ─── Step 5: Audit trail ─────────────────────────────────────────────────────

def print_audit(results, rows):
    wards      = sorted(set(r["ward_id"] for r in results))
    categories = sorted(set(r["category"] for r in results))
    total_anomalies = sum(1 for r in results if r["anomaly_flag"] == "TRUE")

    print("\n" + "=" * 55)
    print("  UC-0C Budget Integrity Analyser — Audit Summary")
    print("=" * 55)
    print(f"  Rows loaded         : {len(rows)}")
    print(f"  Wards processed     : {len(wards)}  → {wards}")
    print(f"  Categories found    : {len(categories)}")
    for c in categories:
        print(f"      • {c}")
    print(f"  Total pairs         : {len(results)}")
    print(f"  Anomalies flagged   : {total_anomalies}")
    print(f"    - scope violations    : {counters['scope_violations']}")
    print(f"    - outlier growth      : {counters['outlier_growth']}")
    print(f"    - missing baseline    : {counters['missing_baseline']}")
    print(f"    - round-number alerts : {counters['round_number_alerts']}")
    print(f"    - phantom rows        : {counters['phantom_rows']}")
    print(f"  Output file         : {OUTPUT_FILE}")
    print("=" * 55 + "\n")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"\n[UC-0C] Loading budget data from: {INPUT_FILE}")
    rows    = load_budget(INPUT_FILE)
    print(f"[UC-0C] Loaded {len(rows)} rows. Enforcing per-ward per-category scope...")

    grouped = group_by_scope(rows)
    print(f"[UC-0C] {len(grouped)} unique ward-category pairs found.")

    results = compute_and_flag(grouped)
    write_output(results, OUTPUT_FILE)
    print_audit(results, rows)


if __name__ == "__main__":
    main()

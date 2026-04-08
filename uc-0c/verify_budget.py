"""
UC-0C Independent Verification Script
Recomputes all ward+category totals from scratch using raw CSV.
Compares against growth_output.csv and flags discrepancies.
"""
import csv
from collections import defaultdict

RAW = r"c:\workspace\prompt-to-production\data\budget\ward_budget.csv"
OUT = r"c:\workspace\prompt-to-production\uc-0c\growth_output.csv"

# Re-aggregate from raw data
totals = defaultdict(float)
missing = defaultdict(int)
row_cnt = defaultdict(int)

with open(RAW, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ward     = row['ward'].strip()
        cat      = row['category'].strip()
        actual   = row['actual_spend'].strip()
        key = (ward, cat)
        row_cnt[key] += 1
        if actual == '':
            missing[key] += 1
        else:
            totals[key] += float(actual)

# Round to 1dp (same as script)
computed = {k: round(v, 1) for k, v in totals.items()}

# Read growth_output.csv
output_rows = {}
with open(OUT, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ward = row['ward'].strip()
        cat  = row['category'].strip()
        total = float(row['total_actual_spend'])
        miss  = int(row['missing_months'])
        output_rows[(ward, cat)] = (round(total, 1), miss)

all_keys = sorted(set(list(computed.keys()) + list(output_rows.keys())))

print(f"{'KEY':<55} {'EXPECTED':>10} {'GOT':>10} {'MISS_EXP':>9} {'MISS_GOT':>9} {'STATUS'}")
print("-" * 110)

errors = []
for key in all_keys:
    ward, cat = key
    exp_total = computed.get(key, 'MISSING')
    exp_miss  = missing.get(key, 0)
    got_total, got_miss = output_rows.get(key, ('MISSING', 'MISSING'))

    if exp_total == 'MISSING':
        status = "❌ EXTRA ROW IN OUTPUT"
        errors.append(f"Extra row: {key}")
    elif got_total == 'MISSING':
        status = "❌ MISSING FROM OUTPUT"
        errors.append(f"Missing row: {key}")
    elif abs(exp_total - got_total) > 0.05:
        status = f"❌ TOTAL MISMATCH"
        errors.append(f"Total mismatch {key}: expected {exp_total}, got {got_total}")
    elif exp_miss != got_miss:
        status = f"❌ MISSING_COUNT MISMATCH (exp={exp_miss}, got={got_miss})"
        errors.append(f"Missing count: {key}")
    else:
        status = "✅ OK"

    label = f"{ward} | {cat}"
    print(f"{label:<55} {str(exp_total):>10} {str(got_total):>10} {exp_miss:>9} {got_miss:>9}  {status}")

print()
print(f"Total groups in raw:    {len(computed)}")
print(f"Total groups in output: {len(output_rows)}")

if errors:
    print(f"\n❌ {len(errors)} ISSUES FOUND:")
    for e in errors:
        print(f"  - {e}")
else:
    print("\n✅ ALL TOTALS VERIFIED CORRECT — No discrepancies found.")

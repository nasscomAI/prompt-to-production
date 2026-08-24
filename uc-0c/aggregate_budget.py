"""
UC-0C: Ward Budget Aggregation
Groups by ward + category, sums actual_spend across all periods.
Missing actual_spend values are EXCLUDED from totals (not treated as zero).
Missing rows are flagged in a separate notes column.
"""

import csv
from collections import defaultdict

INPUT_FILE = r"c:\workspace\prompt-to-production\data\budget\ward_budget.csv"
OUTPUT_FILE = r"c:\workspace\prompt-to-production\uc-0c\growth_output.csv"

# Data structures
totals = defaultdict(float)       # (ward, category) -> sum of actual_spend
missing_count = defaultdict(int)  # (ward, category) -> count of missing actual_spend rows
row_count = defaultdict(int)      # (ward, category) -> total row count

with open(INPUT_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ward = row['ward'].strip()
        category = row['category'].strip()
        actual = row['actual_spend'].strip()
        key = (ward, category)
        row_count[key] += 1
        if actual == '':
            missing_count[key] += 1
        else:
            totals[key] += float(actual)

# Collect all keys in sorted order
all_keys = sorted(totals.keys() | missing_count.keys(), key=lambda x: (x[0], x[1]))

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ward', 'category', 'total_actual_spend', 'missing_months', 'note'])
    for key in all_keys:
        ward, category = key
        total = round(totals[key], 1)
        missing = missing_count[key]
        note = f"{missing} month(s) excluded — actual_spend not reported" if missing > 0 else ""
        writer.writerow([ward, category, total, missing, note])

print(f"Done. Output written to: {OUTPUT_FILE}")
print(f"Total groups: {len(all_keys)}")

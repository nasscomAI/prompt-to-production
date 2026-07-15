import csv
from collections import Counter

ALLOWED = {'Pothole','Flooding','Streetlight','Waste','Noise','Road Damage','Heritage Damage','Heat Hazard','Drain Blockage','Other'}
SEVERITY_KW = ['injury','child','school','hospital','ambulance','fire','hazard','fell','collapse']

with open('results_pune.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print("=== Enforcement Checks ===\n")

# Check 1: All categories in allowed list
bad_cats = [r for r in rows if r['category'] not in ALLOWED]
status1 = "PASS - all categories in allowed list" if not bad_cats else "FAIL: " + str([(r['complaint_id'], r['category']) for r in bad_cats])
print("[1] Category taxonomy:", status1)

# Check 2: Severity keywords -> Urgent
severity_missed = []
for r in rows:
    desc = r['description'].lower()
    has_kw = any(kw in desc for kw in SEVERITY_KW)
    if has_kw and r['priority'] != 'Urgent':
        severity_missed.append((r['complaint_id'], r['priority']))
status2 = "PASS - all severity complaints are Urgent" if not severity_missed else "FAIL: " + str(severity_missed)
print("[2] Severity -> Urgent:", status2)

# Check 3: reason field never empty
no_reason = [r['complaint_id'] for r in rows if not r.get('reason','').strip()]
status3 = "PASS - reason present in all rows" if not no_reason else "FAIL missing: " + str(no_reason)
print("[3] Reason always present:", status3)

# Check 4: NEEDS_REVIEW rows
nr = [(r['complaint_id'], r['category']) for r in rows if r['flag'] == 'NEEDS_REVIEW']
print("[4] NEEDS_REVIEW rows:", nr)

print("\n=== Summary ===")
cats = Counter(r['category'] for r in rows)
pris = Counter(r['priority'] for r in rows)
print("Categories:", dict(cats))
print("Priorities:", dict(pris))
print("Total rows:", len(rows))

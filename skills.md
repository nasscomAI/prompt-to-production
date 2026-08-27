# skills.md — UC-0A: Complaint Classifier

## Skill 1 — `classify_complaint(text)`

**Purpose:** Classify a single complaint string into category + severity + priority.

**Input:** Raw complaint text (string, any length)

**Output:**
```json
{
  "category": "Roads | Water | Sanitation | Electricity | Public Safety | Other",
  "severity": "High | Medium | Low",
  "priority": 1 | 2 | 3
}
```

**Method:** Keyword frequency scoring per department bucket, followed by
two-pass severity escalation (urgency keywords → Medium; safety keywords → High).

**Reliability contract:**
- Any complaint mentioning `injury / child / school / hospital / fire / accident /
  emergency / danger / electric shock / collapse` will ALWAYS be classified High.
- Priority is always deterministic given severity.

---

## Skill 2 — `find_text_column(fieldnames)`

**Purpose:** Auto-detect the complaint text column from CSV headers so the
classifier works across city files with different schemas.

**Logic:** Checks for common column names in priority order:
`complaint → description → text → complaint_text → issue → details → message → content`
Falls back to the last column if none match.

---

## Skill 3 — `process_csv(input_path, output_path)`

**Purpose:** End-to-end pipeline — read input CSV, classify every row,
write enriched output CSV with three new columns: `category`, `severity`, `priority`.

**Guarantees:**
- Input columns are preserved unchanged.
- Duplicate column names are deduplicated.
- Output file is UTF-8 encoded.

---

## Skill 4 — CLI Interface

**Purpose:** Allow the script to run from the terminal with custom input/output paths.

**Usage:**
```bash
# Default (Hyderabad)
python classifier.py

# Custom city
python classifier.py --input data/city-test-files/test_pune.csv

# Custom output path
python classifier.py --input data/city-test-files/test_kolkata.csv --output my_results.csv
```

---

## CRAFT Loop Notes

| Iteration | What failed | What changed |
|-----------|-------------|--------------|
| v1 | No severity differentiation — all complaints got Low | Added two-tier keyword escalation |
| v2 | Safety complaints (injuries, children) under-prioritised | Added hard-High trigger list with `injury/child/school/hospital` |
| v3 | `Other` category too large — many Roads complaints miscategorised | Expanded Roads keyword list with `crater / speed breaker / broken road` |
| v4 (current) | Column auto-detection failed on non-standard CSVs | Added `find_text_column()` with ordered fallback logic |

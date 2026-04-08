# UC-0A Skills

## Skill: classify_complaint

### Description
Classifies one complaint row into category, priority, reason, and flag with strict schema compliance.

### Input
- One complaint row (string description plus optional row id/metadata).

### Output
- category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
- priority: one of Urgent, Standard, Low.
- reason: one sentence citing exact complaint words.
- flag: NEEDS_REVIEW or blank.

### Error and Ambiguity Handling
- If complaint text is empty or unusable, return category=Other, priority=Low, reason explaining missing evidence, flag=NEEDS_REVIEW.
- If multiple categories are equally plausible, return category=Other, flag=NEEDS_REVIEW.
- If severity keywords appear (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), force priority=Urgent.

## Skill: batch_classify

### Description
Reads input CSV, applies classify_complaint row-by-row, and writes output CSV with required columns.

### Input
- --input: path like ../data/city-test-files/test_[city].csv.
- --output: path like results_[city].csv.

### Output
- CSV with one output row per input row, including category, priority, reason, flag.

### Error Handling
- Fail fast if input file is missing.
- Continue row processing on per-row ambiguity by using NEEDS_REVIEW (do not silently drop rows).
- Ensure output always uses exact allowed values.

## RICE Prioritization for Skill Work

| Priority | Improvement | Reach | Impact | Confidence | Effort | RICE Score |
|---|---|---:|---:|---:|---:|---:|
| P1 | Implement shared schema validator used by both skills | 15 | 3 | 0.95 | 1 | 42.75 |
| P2 | Centralize urgency keyword check in classify_complaint | 15 | 3 | 0.9 | 1 | 40.50 |
| P3 | Enforce one-sentence evidence-based reason formatter | 15 | 2 | 0.9 | 1 | 27.00 |
| P4 | Standardize ambiguity fallback (Other + NEEDS_REVIEW) | 15 | 2 | 0.85 | 1 | 25.50 |

# UC-0A Skills

## classify_complaint

**Input:** A single complaint row (dict) with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open

**Output:** A dict with fields: complaint_id, category, priority, reason, flag

**Logic:**
1. Normalize description to lowercase for matching.
2. Match against category keyword rules (first match wins based on priority order).
3. Scan for severity keywords — if any found, set priority to Urgent.
4. Build reason string citing the matched keywords from the original description.
5. Check if multiple categories match — if yes, set flag to NEEDS_REVIEW.
6. Return the classification result.

**Enforcement:**
- Category must be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
- Priority must be one of: Urgent, Standard, Low.
- Severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

---

## batch_classify

**Input:** input_path (str), output_path (str)

**Output:** CSV file written to output_path

**Logic:**
1. Read input CSV using csv.DictReader.
2. For each row, call classify_complaint.
3. If a row throws an error, catch it and produce a fallback result with NEEDS_REVIEW flag.
4. Write all results to output CSV with headers: complaint_id, category, priority, reason, flag.
5. Print count of classified complaints.

**Enforcement:**
- Must not crash on bad rows.
- Must produce output even if some rows fail.
- Must flag null/missing data rows.

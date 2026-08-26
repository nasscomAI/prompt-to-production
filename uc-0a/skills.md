# UC-0A — skills.md (Complaint Classifier)

Two skills, generated from the prompt then refined.

## skill: classify_complaint
**Purpose:** Classify ONE complaint row.
**Input:** a single complaint row (dict) with a `description` field.
**Output:** { category, priority, reason, flag }
**Logic:**
1. Lower-case the description.
2. Match category against the fixed keyword table. First match by the table's
   priority order wins. No match -> `Other` + NEEDS_REVIEW.
3. Validate category against the allowed list (Pothole, Flooding, Streetlight,
   Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage,
   Other). Anything else -> `Other`.
4. Scan for severity keywords (injury, child, school, hospital, ambulance,
   fire, hazard, fell, collapse). Any hit -> priority = Urgent.
   Else: Standard for a real category, Low for Other.
5. If the description matches two conflicting categories, set flag = NEEDS_REVIEW.
6. Build a one-sentence reason that quotes the matched keyword(s).

## skill: batch_classify
**Purpose:** Apply classify_complaint across a whole CSV.
**Input:** input CSV path, output CSV path.
**Output:** writes results CSV with category, priority, reason, flag columns
appended; prints a summary (row count, Urgent count, NEEDS_REVIEW count).
**Logic:**
1. Read input CSV with DictReader.
2. For each row, call classify_complaint and merge the verdict in.
3. Write all rows back out, preserving original columns + the 4 new ones.

# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag.
    input: A dict representing one input CSV row (description plus ward, location, city, date_raised, reported_by, days_open).
    output: A dict with exactly four fields — category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent or Standard), reason (one sentence quoting words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: When no category keyword matches, output category Other with flag NEEDS_REVIEW; when the description is missing or the row is malformed, fail safe with category Other, flag NEEDS_REVIEW, and never raise.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to every row, and write the results CSV.
    input: Input path to a read-only test_[city].csv and output path to write results_[city].csv.
    output: A CSV containing every input column plus category, priority, reason, flag columns, one row per input row, written even if some rows fail.
    error_handling: Never crashes on bad rows or missing fields; a failed row still gets a written output row classified as Other/NEEDS_REVIEW; no attempt to read category or priority_flag columns.
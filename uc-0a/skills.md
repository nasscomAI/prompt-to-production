skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row by assigning category, priority,
      reason, and optional review flag from the complaint description alone,
      following UC-0A enforcement rules.
    input: >
      A dict representing one CSV row from test_[city].csv. Required key:
      description (string). Optional passthrough keys include complaint_id,
      date_raised, city, ward, location, reported_by, days_open. Must not
      depend on stripped category or priority_flag columns.
    output: >
      A dict with keys complaint_id (string, echoed from input),
      category (exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (Urgent, Standard, or Low), reason (one sentence citing specific
      words from description), and flag (NEEDS_REVIEW or blank string).
    error_handling: >
      If description is missing, empty, or null, return category Other,
      priority Standard, reason noting the missing description, and flag
      NEEDS_REVIEW. If category is genuinely ambiguous, return category Other
      with flag NEEDS_REVIEW rather than guessing. If a severity keyword
      (injury, child, school, hospital, ambulance, fire, hazard, fell,
      collapse) appears in the description, priority must be Urgent regardless
      of category uncertainty. Never raise on a single bad row; always return
      a complete output dict.

  - name: batch_classify
    description: >
      Read a city test CSV, apply classify_complaint to each row, and write
      a results CSV with one classified output row per input row.
    input: >
      input_path (string): path to ../data/city-test-files/test_[city].csv
      (15 rows, no category or priority_flag columns).
      output_path (string): path to write uc-0a/results_[city].csv.
    output: >
      A CSV file at output_path with columns complaint_id, category, priority,
      reason, flag — one row per successfully processed input row, row count
      matching input row count.
    error_handling: >
      Do not crash the batch on individual row failures. For unreadable or
      malformed rows, write an output row with category Other, priority
      Standard, reason describing the parse failure, and flag NEEDS_REVIEW.
      Flag null or empty description fields via classify_complaint error
      handling. If the input file is missing or not valid CSV, raise a clear
      file-level error before writing partial output. Continue processing
      remaining rows after any per-row failure so the output file is always
      produced for valid input files.

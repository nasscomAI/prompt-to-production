# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into category, priority, reason, and
      flag according to the UC-0A taxonomy and severity rules.
    input: |
      dict with keys: complaint_id, description, and any other passthrough
      columns from the source CSV.
    output: |
      dict with keys: complaint_id, category, priority, reason, flag.
      category is one of 10 allowed strings; priority is Urgent/Standard/Low;
      reason is a single sentence citing description words; flag is
      NEEDS_REVIEW or blank.
    error_handling: >
      If description is missing or empty, set category to Other, priority to
      Low, flag to NEEDS_REVIEW, and reason to "No description provided."

  - name: batch_classify
    description: >
      Read an input CSV row by row, apply classify_complaint to each, and
      write the results CSV with all original columns plus classification
      columns appended.
    input: |
      input_path (str) — path to test CSV with complaint rows.
      output_path (str) — path to write results CSV.
    output: |
      CSV file written to output_path with columns: complaint_id, description,
      (any original passthrough columns), category, priority, reason, flag.
    error_handling: >
      Skips rows that fail to parse without crashing. Logs skipped rows to
      stderr. Always writes partial results — never leaves output file empty
      if at least one row succeeded.

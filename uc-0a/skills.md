# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority, reason,
      and flag according to the schema in agents.md.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open.
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
    error_handling: >
      If input is missing required keys, raises ValueError with missing key
      names. If category cannot be determined, returns category: Other and
      flag: NEEDS_REVIEW. Never crashes — captures errors in a failed_rows
      accumulator in batch context.

  - name: batch_classify
    description: >
      Read a CSV of complaint rows, apply classify_complaint to each row,
      and write the results to an output CSV.
    input: >
      input_path (str): path to CSV with columns complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open.
    output: >
      Writes CSV to output_path with columns: complaint_id, category, priority,
      reason, flag. Also prints count of failed rows (if any).
    error_handling: >
      If the input file is missing or unreadable, raises FileNotFoundError.
      If a row is malformed, it is skipped and counted in a failed_rows
      counter — other rows still process. At least one row must succeed, or
      no output file is written and an error is raised.

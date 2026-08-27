skills:
  - name: classify_complaint
    description: >
      Classify one complaint row into category, priority, reason, and flag
      based on keyword rules in the description field.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      category is one of 10 allowed strings; priority is Urgent if severity
      keywords present, else Standard; reason is a sentence citing >=3 words
      from description; flag is blank or NEEDS_REVIEW.
    error_handling: >
      If description is missing or empty, return category: Other, priority:
      Standard, flag: NEEDS_REVIEW. Never raise an exception — return a dict
      for every input.

  - name: batch_classify
    description: >
      Read an input CSV, apply classify_complaint to every row, and write a
      results CSV with columns: complaint_id, category, priority, reason, flag.
    input: >
      input_path (str) — path to CSV with complaint_id and description columns.
      output_path (str) — path to write results CSV.
    output: >
      Writes a CSV file to output_path. Prints completion message to stdout.
    error_handling: >
      Skip rows with missing complaint_id or description, write a warning to
      stderr, but continue processing remaining rows. Always produce an output
      file even if some rows fail.

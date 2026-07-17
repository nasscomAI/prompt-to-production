# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into category, priority, reason, and flag
      based solely on the description and other row fields.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
    error_handling: >
      If description is empty or None, set category to Other, flag to
      NEEDS_REVIEW, reason to "Empty description". Never raise an exception.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to each row,
      and write the results CSV with columns complaint_id, category, priority,
      reason, flag.
    input: >
      input_path (str) — path to CSV with complaint rows; output_path (str) —
      path to write results CSV
    output: >
      A CSV file written to output_path with the header and one row per input
      row. Prints "Done. Results written to {output_path}" on completion.
    error_handling: >
      Rows with missing or corrupt data are classified with category: Other,
      flag: NEEDS_REVIEW, and reason describing the error. Never crash on a bad
      row — always produce output for every input row.

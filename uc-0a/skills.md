skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority, reason, and flag
      using keyword-based rules on the description field.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
    error_handling: >
      Returns complaint_id with category=Other, flag=NEEDS_REVIEW if description is missing,
      empty, or contains no matching keywords. Never crashes.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to every row,
      and write the results to an output CSV.
    input: >
      input_path (str) — path to test CSV; output_path (str) — path for results CSV
    output: >
      Writes a CSV file with header: complaint_id, category, priority, reason, flag
    error_handling: >
      Does not crash on malformed rows. Writes a fallback row for any row that causes an
      exception and continues processing remaining rows. Always writes the output file.

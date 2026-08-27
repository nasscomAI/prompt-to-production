# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row dict into category, priority, reason, and
      flag according to the UC-0A schema.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
    error_handling: >
      If description is empty or missing, set category to Other, priority to
      Standard, reason to "No description provided", and flag to NEEDS_REVIEW.
      For ambiguous descriptions, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to every row,
      and write a results CSV with category, priority, reason, and flag columns.
    input: >
      input_path (str): path to the input CSV with columns complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open
    output: >
      output_path (str): path where the results CSV is written with columns
      complaint_id, category, priority, reason, flag
    error_handling: >
      Does not crash on malformed rows — sets flag NEEDS_REVIEW for any row
      that cannot be processed. Produces partial output even if some rows fail.

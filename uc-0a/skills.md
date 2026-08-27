skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row by assigning a category, priority,
      reason, and optional flag based on the description text.
    input: >
      dict — a single row from the input CSV with keys: complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open.
    output: >
      dict — with keys: complaint_id, category, priority, reason, flag. Category
      is one of 10 allowed values. Priority is Urgent/Standard/Low. Reason is a
      one-sentence explanation citing words from the description. Flag is either
      NEEDS_REVIEW or blank.
    error_handling: >
      If description is empty or missing, set category: Other, priority: Low,
      flag: NEEDS_REVIEW. If the description maps to no clear category, set
      category: Other and flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint to each
      row, and write the results to an output CSV.
    input: >
      input_path — string path to a CSV file with columns: complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open.
      output_path — string path where the results CSV will be written.
    output: >
      Writes a CSV file at output_path with columns: complaint_id, category,
      priority, reason, flag. One row per input row, in the same order.
    error_handling: >
      If the input file cannot be read or is malformed, raise a clear error
      message. If a single row fails classification, set category: Other,
      flag: NEEDS_REVIEW for that row and continue processing remaining rows.
      Never crash on a bad row — always produce output for all rows.

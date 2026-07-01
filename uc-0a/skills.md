skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into category, priority, reason, and flag.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag
    error_handling: >
      Returns category: Other, priority: Standard, flag: NEEDS_REVIEW on any error

  - name: batch_classify
    description: >
      Read an input CSV of complaints, classify every row using classify_complaint,
      and write the results to an output CSV.
    input: >
      input_path (str) — path to CSV with complaint rows;
      output_path (str) — path to write results CSV
    output: >
      Writes CSV file to output_path with columns: complaint_id, category, priority,
      reason, flag
    error_handling: >
      Processes all rows independently; a single bad row does not crash the batch.
      Failed rows get flag: NEEDS_REVIEW.

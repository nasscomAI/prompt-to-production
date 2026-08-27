skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag.
    input: dict with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: >
      If description is empty or missing, return category: Other, priority: Standard,
      reason: "Empty description", flag: NEEDS_REVIEW. If category is ambiguous,
      return category: Other with flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each row, and writes results to an output CSV.
    input: input_path (string, path to CSV), output_path (string, path to write results CSV)
    output: Writes a CSV file with columns complaint_id, category, priority, reason, flag
    error_handling: >
      Skips rows with fatal parse errors but does not crash. Logs warnings for
      skipped rows. Produces output even if some rows fail. Missing columns
      raise a clear error before processing.

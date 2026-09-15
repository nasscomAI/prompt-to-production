skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using only its description text.
    input: A dict for one CSV row with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys complaint_id, category, priority, reason, flag, where category and priority are from the fixed allowed lists and reason quotes words from description.
    error_handling: If description is missing or empty, returns category "Other", priority "Low", reason "no description provided", flag "NEEDS_REVIEW". If description matches multiple categories or none clearly, returns category "Other" and flag "NEEDS_REVIEW" instead of guessing.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (str, path to test_[city].csv) and output_path (str, path to write results CSV).
    output: Writes a CSV file at output_path with columns complaint_id, category, priority, reason, flag, one row per input row.
    error_handling: If a row is malformed (missing/extra columns) or CSV parsing fails for a row, that row is written with category "Other", priority "Low", flag "NEEDS_REVIEW" and processing continues for remaining rows rather than crashing the whole batch.

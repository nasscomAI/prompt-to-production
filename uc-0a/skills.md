skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to the fixed schema and severity keyword rules.
    input:
      type: dict
      format: "A single CSV row as a dict, at minimum containing a 'description' field (str) and 'complaint_id'"
    output:
      type: dict
      format: "{complaint_id, category: one of the 10 allowed values, priority: Urgent/Standard/Low, reason: str citing description words, flag: 'NEEDS_REVIEW' or ''}"
    error_handling: >
      If the description field is missing or empty, set category to 'Other',
      priority to 'Low', reason to 'No description provided', and flag to
      'NEEDS_REVIEW' rather than guessing a category. If the description
      contains a severity keyword but the category is otherwise unclear, still
      apply Urgent priority — severity detection is independent of category
      confidence.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV — without crashing on any single bad row.
    input:
      type: file paths
      format: "input_path (str) to test_[city].csv, output_path (str) for results_[city].csv"
    output:
      type: CSV file
      format: "One row per input row, columns: complaint_id, category, priority, reason, flag — written to output_path"
    error_handling: >
      If the input file does not exist, raise a clear error and stop
      execution. If an individual row causes an unexpected error during
      classification, catch it, classify that row as category='Other',
      flag='NEEDS_REVIEW', reason describing the processing error, and
      continue processing the remaining rows rather than crashing the whole
      batch.

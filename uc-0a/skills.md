skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, reason, and flag.
    input: "A string containing the complaint description (e.g., from a CSV row)."
    output: "A structured dictionary/object containing: category, priority, reason, flag."
    error_handling: "If the description is empty or nonsense, set category to 'Other', priority to 'Low', and flag to 'NEEDS_REVIEW'."

  - name: batch_classify
    description: Reads complaint descriptions from an input CSV and applies classification to each row, writing results to an output CSV.
    input: "Path to an input CSV file with a 'description' column."
    output: "Path to an output CSV file with additional columns: category, priority, reason, flag."
    error_handling: "Rows with missing descriptions are skipped; errors in individual row processing are logged, allowing the batch to continue."

skills:
  - name: classify_complaint
    description: Classifies a single complaint row using the LLM and RICE enforcement rules to extract category, priority, reason, and flag.
    input: dict containing complaint row data (must include keys 'complaint_id' and 'description').
    output: dict with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is missing or null, defaults to category: 'Other', priority: 'Low', reason: 'Missing complaint description.', flag: 'NEEDS_REVIEW'. If the LLM call fails, returns fallback values with flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads all rows from the input CSV file, processes them row-by-row using classify_complaint, and writes the results to the output CSV file.
    input: input_path (str) to the source CSV, output_path (str) to the destination CSV.
    output: Writes a CSV file containing columns: 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Handles missing input file gracefully, skips completely malformed rows with warning logs instead of crashing, and guarantees that valid rows are classified and written to the output file even if some rows fail.

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to assign a category, priority level, citation-backed reason, and ambiguity flag.
    input: A dictionary representing a row of the citizen complaint dataset (with a 'description' field).
    output: A dictionary containing the fields 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Falls back to category 'Other', priority 'Standard', and flag 'NEEDS_REVIEW' if the input description is missing or empty.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, processes each row using the classify_complaint skill, and writes the results to an output CSV file.
    input: Paths to the input CSV file and the output CSV file.
    output: None (writes results to the specified output path).
    error_handling: Catches row-level processing errors and writes default error values for the failed row to ensure the batch process does not crash.

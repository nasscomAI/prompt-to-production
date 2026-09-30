skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag using rule-based parsing.
    input: A dictionary representing a single row from the complaint CSV (containing at least 'complaint_id' and 'description').
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is blank or the category cannot be clearly determined or matches multiple categories, the category is set to 'Other' and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of citizen complaints, processes each row using classify_complaint, and writes the results to an output CSV.
    input: File paths for input CSV (test_[city].csv) and output CSV (results_[city].csv).
    output: None (writes results to output CSV file).
    error_handling: Handles missing input files, logs warnings for rows with missing IDs or blank descriptions, and continues processing other rows rather than crashing.

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and classifies its category, priority, reason, and review flag based on strict criteria.
    input: A dictionary representing a single row from the complaints CSV (must contain 'complaint_id' and 'description').
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty or missing, it defaults category to 'Other', priority to 'Standard', reason to a warning message, and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an input CSV file of complaints, applies the classification to each row, and writes the results to an output CSV file.
    input: Two strings specifying the input CSV file path and output CSV file path.
    output: None (writes results to the specified output CSV).
    error_handling: Catches file reading errors, processes valid rows while logging warnings for corrupted rows, and ensures the output file is created successfully.

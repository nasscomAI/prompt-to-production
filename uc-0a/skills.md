skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag using predefined keyword and logic checks.
    input: A dictionary representing a single row from the complaint CSV file, with keys like 'complaint_id' and 'description'.
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If description is null or empty, category is set to 'Other', priority is set to 'Low', reason is set to 'Missing description', and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Path to input CSV file and path to output CSV file as strings.
    output: Writes a CSV file containing classified results and returns None.
    error_handling: If a row fails to process, it is logged, and classification continues to ensure the output CSV is generated even if some rows are invalid.

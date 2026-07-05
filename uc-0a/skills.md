skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row to extract and validate the category, priority, reason, and review flag.
    input: A dictionary representing a single row from the complaint CSV, containing at least the key 'description'.
    output: A dictionary containing the keys: 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the complaint description is empty, missing, or extremely vague, sets the category to 'Other', priority to 'Low', reason to 'Empty or invalid description provided.', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file containing multiple citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: Path to the input CSV file containing citizen complaints, and path to the output CSV file to write.
    output: None (writes a CSV file with columns: complaint_id, category, priority, reason, flag).
    error_handling: Handles empty files, invalid CSV formats, or missing columns by raising clean error messages, and ensures that if a single row fails to classify, it does not crash the entire batch process.

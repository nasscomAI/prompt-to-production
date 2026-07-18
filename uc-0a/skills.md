skills:
  - name: classify_complaint
    description: Classifies a single complaint description into one of the predefined categories and priorities, citing specific keywords.
    input: A dictionary representing a single CSV row with at least a 'description' field.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty or missing, categories are defaulted to 'Other', priority is 'Low', and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV file, applying classify_complaint to each row and writing the output to a CSV file.
    input: Absolute or relative file paths to input CSV and output CSV.
    output: None (writes results to output CSV file).
    error_handling: Handles empty or invalid rows gracefully without crashing, flagging any problematic rows as NEEDS_REVIEW, and continues processing the rest of the batch.

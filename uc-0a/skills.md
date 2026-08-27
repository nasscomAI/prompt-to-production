skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to determine its category, priority, reason, and review flag based on strict enforcement rules.
    input:
      type: dict
      format: A dictionary representing a CSV row with keys like 'complaint_id', 'description', etc.
    output:
      type: dict
      format: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If the description is missing or empty, set category to 'Other', priority to 'Standard', reason to 'Empty description', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes the results to the output CSV file.
    input:
      type: str
      format: Absolute or relative file paths for input CSV and output CSV.
    output:
      type: None
      format: Writes a CSV file containing the classified complaints.
    error_handling: Skips malformed rows or rows missing 'complaint_id' and prints a warning, ensuring the rest of the batch is processed without crashing.

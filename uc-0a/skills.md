skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag.
    input:
      type: dict
      format: A dictionary representing a row from the complaint CSV, containing at least the 'description' and 'complaint_id' keys.
    output:
      type: dict
      format: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling:
      rules:
        - "If description is missing, empty, or null, classify category as 'Other', priority as 'Standard', reason as 'Missing description', and flag as 'NEEDS_REVIEW'."
        - "If the category is genuinely ambiguous or cannot be determined, output category: 'Other' and flag: 'NEEDS_REVIEW'."

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes the results to the output CSV file.
    input:
      type: dict
      format: A dictionary containing 'input_path' (string) and 'output_path' (string).
    output:
      type: bool
      format: True if execution succeeded and output CSV was successfully created, False or error raised otherwise.
    error_handling:
      rules:
        - "Do not crash on bad or corrupt rows; log the error and continue processing other rows."
        - "Flag nulls or missing fields within rows and proceed."
        - "Ensure the output file is always written even if some rows fail to classify."

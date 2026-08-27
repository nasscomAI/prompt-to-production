skills:
  - name: classify_complaint
    description: Analyzes a single complaint row's description to determine its category, priority, justification, and review flag.
    input:
      type: dict
      format: "Keys: complaint_id (str), description (str), and other CSV fields."
    output:
      type: dict
      format: "Keys: complaint_id (str), category (str), priority (str), reason (str), flag (str)."
    error_handling: >
      If description is empty or missing, set category to 'Other', priority to 'Low', reason to 'Empty description', and flag to 'NEEDS_REVIEW'.
      If category is ambiguous, assign the most likely category or 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes the results to the output CSV file.
    input:
      type: str
      format: "Path to input CSV file containing citizen complaints."
    output:
      type: str
      format: "Path to output CSV file containing classified results."
    error_handling: >
      If input file is missing or empty, raise an appropriate FileNotFoundError.
      If a row has missing or malformed fields, flag the row using default values and log the error, but do not crash. Ensure all successful rows are written.

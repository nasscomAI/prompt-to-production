

skills:
  - name: classify_complaint
    description: Processes a single complaint description and returns a structured classification.
    input: String (the complaint description text).
    output: Object containing category, priority, reason, and flag.
    error_handling: Returns 'Other' category and 'NEEDS_REVIEW' flag if the description is empty or indecipherable.

  - name: batch_classify
    description: Reads a CSV file of complaints and processes each row using classify_complaint.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file.
    error_handling: Logs rows that fail to process and continues with the remaining dataset.

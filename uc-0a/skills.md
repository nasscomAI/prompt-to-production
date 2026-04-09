# skills.md

skills:
  - name: classify_complaint
    description: Classified a single citizen complaint into a category, priority, and provides a justification reason.
    input: A single complaint row (string description).
    output: A JSON object containing category, priority, reason, and flag.
    error_handling: If the description is empty or nonsense, set category to 'Other', priority to 'Low', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an input CSV file of complaints and writes the classification results to an output CSV file.
    input: Path to the input CSV file.
    output: Creation of an output CSV file at the specified results path.
    error_handling: Ensure the output directory exists; if a row fails individual classification, log the error and continue processing remaining rows.

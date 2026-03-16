skills:
  - name: classify_complaint
    description: Classifies a single complaint description into a category and priority level.
    input: A dictionary representing a complaint row from the CSV file, containing complaint_id and description fields.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is empty, missing, or ambiguous, the function assigns category as Other, priority as Low or Standard, and sets flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each complaint row, and writes the structured results to an output CSV file.
    input: Path to an input CSV file containing complaint records.
    output: A new CSV file containing classification results with complaint_id, category, priority, reason, and flag fields.
    error_handling: If a row cannot be processed due to invalid data or runtime error, the row is still written to output with category set to Other and flag set to NEEDS_REVIEW so that processing continues without crashing.
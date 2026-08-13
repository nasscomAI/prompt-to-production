skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag fields.
    input: A string description of the citizen complaint.
    output: A dictionary or object containing category (string), priority (string), reason (string), and flag (string or null).
    error_handling: If the description is empty, invalid, or extremely ambiguous, set category to "Other", priority to "Low", reason to "Empty/ambiguous description", and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Read an input CSV file containing citizen complaints, classify each complaint row, and write the results to an output CSV file.
    input: Path to the input CSV file.
    output: Path to the output CSV file containing the original fields plus category, priority, reason, and flag.
    error_handling: Log errors for missing input files or malformed CSV rows. Ensure the process continues even if individual rows fail, marking failed rows with category "Other" and flag "NEEDS_REVIEW".

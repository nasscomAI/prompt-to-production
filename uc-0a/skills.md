skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category and priority.
    input: A single string representing the complaint description.
    output: An object containing four fields: category (exact string from the allowed list), priority (Urgent, Standard, or Low), reason (a single sentence citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If the category cannot be determined from the description alone, outputs category 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of citizen complaints from an input CSV, classifies each row, and writes the results to an output CSV.
    input: Filepath to an input CSV containing complaint rows.
    output: Filepath to the generated output CSV with the added classification columns (category, priority, reason, flag).
    error_handling: If an input row is malformed, skips the invalid row or writes blank classification values, allowing processing of the remaining CSV to continue.

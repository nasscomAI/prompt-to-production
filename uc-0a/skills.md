# skills.md

skills:

  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category and priority with a justified reason and ambiguity flag.
    input: A single complaint row as a dictionary containing complaint_id and description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or invalid, return category Other, priority Standard, a reason stating that the description is missing or invalid, and flag NEEDS_REVIEW. If the category is genuinely ambiguous, return category Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read complaint rows from an input CSV, classify each row using classify_complaint, and write the results to an output CSV.
    input: Input CSV file path containing complaint rows with complaint_id and description columns.
    output: Output CSV containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Do not crash on missing or malformed rows. Flag invalid rows with NEEDS_REVIEW and continue processing the remaining rows so an output CSV is still produced.
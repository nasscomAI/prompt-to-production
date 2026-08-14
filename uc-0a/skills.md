skills:
  - name: classify_complaint
    description: Classify one complaint row into the allowed category and priority schema.
    input: A dictionary containing complaint_id and complaint metadata including description and location.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, return category Other and flag NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Read the input CSV, classify each complaint row, and write the result CSV.
    input: Input CSV path and output CSV path.
    output: A CSV file containing one output row per complaint with the required fields.
    error_handling: If a row cannot be processed normally, still write a row with complaint_id, category Other, priority Standard, a reason describing the issue, and flag NEEDS_REVIEW.

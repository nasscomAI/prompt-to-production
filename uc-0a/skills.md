skills:

  - name: classify_complaint
    description: Classifies one citizen complaint into a category and priority and provides a reason and review flag.
    input: A single complaint row containing the complaint description.
    output: A classification result containing category, priority, reason, and flag.
    error_handling: If the category is genuinely ambiguous, use Other and NEEDS_REVIEW instead of guessing or inventing a category.

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: A CSV file containing multiple complaint rows with complaint descriptions.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for each complaint.
    error_handling: If a row cannot be processed, create an Other and NEEDS_REVIEW result and continue processing the remaining rows.
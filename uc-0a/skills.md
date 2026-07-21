skills:
  - name: classify_complaint
    description: Classifies one complaint row into the UC-0A taxonomy with a priority, reason, and review flag.
    input: A dict-like complaint row containing complaint_id plus source fields such as description, location, ward, city, and days_open.
    output: A dict with keys complaint_id, category, priority, reason, and flag using only the allowed schema values.
    error_handling: Missing or blank descriptions return category Other with flag NEEDS_REVIEW and a reason that names the missing evidence; ambiguous text also returns NEEDS_REVIEW instead of a guessed category.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a resilient results CSV.
    input: An input CSV path and an output CSV path.
    output: A CSV whose rows contain complaint_id, category, priority, reason, and flag for each source complaint.
    error_handling: It never aborts the batch on a bad row; row-level failures are converted into Other plus NEEDS_REVIEW with an explanatory reason and the batch still writes all rows.

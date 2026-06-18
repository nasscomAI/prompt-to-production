skills:
  - name: classify_complaint
    description: Classifies one municipal complaint row into the fixed category taxonomy, priority, reason, and review flag.
    input: A CSV row represented as a dictionary with complaint_id, city, ward, location, description, reported_by, and days_open fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing or the complaint is ambiguous, return category Other and flag NEEDS_REVIEW instead of failing.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint to each row, and writes a results CSV.
    input: An input CSV path and an output CSV path.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Catches row-level failures, writes a fallback Other plus NEEDS_REVIEW result for that row, and continues processing the remaining rows.

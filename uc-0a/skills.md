skills:
  - name: classify_complaint
    description: Classifies a single complaint row into an approved category and returns the required output fields.
    input: A complaint row dictionary with at least a description field and optionally complaint_id, location, and ward.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is blank or unclear, return category Other and flag NEEDS_REVIEW instead of failing.

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: An input CSV path and an output CSV path.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for each row.
    error_handling: Continues processing even when individual rows are malformed and writes a review row for failed cases.

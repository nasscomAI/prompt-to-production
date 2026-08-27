# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into an approved category with urgency, reason, and a review flag.
    input: A dictionary representing one CSV row with at least complaint_id and description fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or unreadable, return category Other, priority Standard, and set flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a complaint CSV, applies the classification logic to each row, and writes a results CSV.
    input: An input CSV path and an output CSV path.
    output: A CSV file containing one classified row per input row.
    error_handling: If a row fails to parse, keep processing the rest of the file and mark that row as Other with NEEDS_REVIEW.

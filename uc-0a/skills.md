# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into a civic category, severity priority, reason, and review flag.
    input: A single dictionary-like row from a CSV with at least a complaint_id and description field.
    output: A dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: If the row is malformed or the description is missing, return category Other, priority Standard, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes a results CSV file.
    input: A path to an input CSV file and a path to an output CSV file.
    output: A CSV file with the same number of rows as the input, preserving output even when some rows fail.
    error_handling: If a row fails during classification, emit a fallback row with category Other and flag NEEDS_REVIEW instead of crashing the pipeline.

# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into the required schema.
    input: A single CSV row dictionary that includes at least a description field.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or the row is malformed, return a safe fallback with category Other, priority Standard, reason noting the missing input, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV, classify each complaint row, and write an output CSV.
    input: A path to an input CSV file and a path for the output CSV file.
    output: An output CSV file with the required columns and one row per input complaint.
    error_handling: Continue processing after bad rows, write a fallback row for failures, and create the output directory if needed.

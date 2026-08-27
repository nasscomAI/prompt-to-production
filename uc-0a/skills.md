# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag based on predefined taxonomies and rules.
    input: A dictionary representing a single row from the citizen complaints CSV (must contain complaint_id and description).
    output: A dictionary containing keys complaint_id, category, priority, reason, and flag.
    error_handling: If required inputs are missing or empty, set category to Other, priority to Standard, reason to Invalid input, and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read citizen complaints from an input CSV file, classify each row using classify_complaint, and write the output to a new CSV file.
    input: Path to the input CSV file (string) and path to write the output CSV file (string).
    output: Writes a CSV file containing columns complaint_id, category, priority, reason, and flag.
    error_handling: If the input file is not found, raise an error. If individual rows fail to classify, log the failure, flag the row with NEEDS_REVIEW, and continue processing other rows.

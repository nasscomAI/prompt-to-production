# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description to assign a category, priority level, and reason based on the defined schema.
    input: String (citizen complaint description)
    output: Structured object containing category (String), priority (String), reason (String), and flag (String)
    error_handling: If category cannot be determined, returns Category: Other and Flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file and processes each row using the classify_complaint skill, writing the final results to an output CSV.
    input: Path to input CSV file (e.g., ../data/city-test-files/test_pune.csv)
    output: Path to output CSV file (e.g., uc-0a/results_pune.csv)
    error_handling: Continues processing remaining rows if one row fails; logs errors for any malformed input rows.

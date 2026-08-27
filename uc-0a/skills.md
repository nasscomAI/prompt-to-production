skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a specific category, priority, reason, and flag.
    input: One complaint row (text description)
    output: Category, priority, reason, and flag
    error_handling: If category cannot be determined from description alone, output category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV file path
    output: Output CSV file path
    error_handling: If a row fails or input file is missing/invalid, logs the error and skips or halts appropriately.

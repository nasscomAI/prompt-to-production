skills:
  - name: classify_complaint
    description: Receives one complaint row and outputs the classified category, priority, reason, and flag.
    input: One complaint row (dictionary or string) containing the complaint details.
    output: JSON object or dictionary containing category, priority, reason, and flag out.
    error_handling: If input format is invalid or category truly unrecognizable, return category="Other" and flag="NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint per row, and writes output to a results CSV file.
    input: File paths to input CSV and output CSV.
    output: Creates the output CSV with the added classification columns.
    error_handling: If a row parsing fails, skip it or default to Review, and continue processing to ensure the batch output file is generated.

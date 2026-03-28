skills:
  - name: classify_complaint
    description: Processes a single unstructured citizen complaint description to determine its category, priority, reason, and review flag.
    input: A single string containing the unstructured complaint description.
    output: A structured record containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the input is invalid or ambiguous, output category as "Other" and set the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the structured classification to an output CSV.
    input: File paths for the input CSV (e.g., ../data/city-test-files/test_[your-city].csv) and the desired output CSV.
    output: A newly created output CSV file containing the classifications.
    error_handling: If a row fails to process or is malformed, gracefully handle the error and proceed to the next row.

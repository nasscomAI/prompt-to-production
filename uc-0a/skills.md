# skills.md

skills:
  - name: classify_complaint
    description: Parses a single unstructured citizen complaint description and maps it to structured classification fields.
    input: A single citizen complaint description (string).
    output: A structured record containing category, priority, reason, and flag fields.
    error_handling: If the description is genuinely ambiguous, set the flag field to "NEEDS_REVIEW" and do a best-effort classification or set category to "Other".

  - name: batch_classify
    description: Reads an input CSV file, applies the classifier logic to each row, and writes the combined output to a new CSV file.
    input: Path to the input CSV file (e.g., ../data/city-test-files/test_[city].csv) and the desired output CSV file path.
    output: A generated CSV file containing the classified rows.
    error_handling: Skip rows that are irreparably malformed and log them; continue processing other rows.

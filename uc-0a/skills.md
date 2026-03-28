skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and flag.
    input: A single citizen complaint record containing the description.
    output: A dictionary or object containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the input is genuinely ambiguous, set the flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the categorized data to an output CSV.
    input: File path to the input CSV containing citizen complaints.
    output: File path to the generated output CSV file.
    error_handling: If a row cannot be processed, log the error, skip the malformed row, and continue processing the rest of the CSV.

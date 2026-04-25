skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into predefined fields.
    input: A dictionary representing a single row from the complaints CSV.
    output: A dictionary containing four fields: category, priority, reason, and flag.
    error_handling: If the input is invalid or the category is genuinely ambiguous, return category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV containing the original complaint_id and the 4 classified fields.
    input: File path to the input CSV file.
    output: File path to the written output CSV file.
    error_handling: If a row fails processing or is malformed, log the error and write an error entry for that row in the output CSV.

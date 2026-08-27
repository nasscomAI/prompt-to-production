skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a structured category, priority, reason, and flag.
    input: A single citizen complaint text description.
    output: A structured object containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the complaint description is completely ambiguous or irrelevant, output category as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV (`--input`) and the output CSV (`--output`).
    output: A newly generated output CSV file containing all rows with their respective classifications.
    error_handling: If a row is malformed or classification fails, log an error for that row, flag it as NEEDS_REVIEW, and continue processing the rest of the CSV.


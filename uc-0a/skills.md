# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category and sets priority, reason, and flag.
    input: A string representing one complaint row description.
    output: A dictionary containing category, priority, reason, and flag out.
    error_handling: If input is invalid or ambiguous, output category as "Other" and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes to an output CSV.
    input: Path to the input CSV file.
    output: Generates a results CSV file matching the output format constraints.
    error_handling: Skips unparsable rows, logging the error, but continues classification for the rest of the file.

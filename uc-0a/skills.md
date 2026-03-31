# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A single complaint row containing a description.
    output: A structured object containing category, priority, reason, and flag.
    error_handling: If the description is genuinely ambiguous, sets flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to an input CSV file containing citizen complaints.
    output: Path to the generated output CSV file containing classified results.
    error_handling: If input file is missing or malformed, raises an error. If a row fails to classify properly, logs the error and proceeds to the next row, setting flag to NEEDS_REVIEW.

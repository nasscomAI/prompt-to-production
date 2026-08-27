skills:
  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, reason, and whether it needs review.
    input: A single citizen complaint row or description text string.
    output: A structured record containing `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the input is genuinely ambiguous or lacks clear categorization details, output category as "Other" and set the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the classified data to an output CSV.
    input: Path to an input CSV file containing multiple complaint rows.
    output: Path to an output CSV file containing the classifications.
    error_handling: If a row is malformed or missing a description, log the error for that row, flag the output if appropriate, and safely continue processing the rest of the CSV.

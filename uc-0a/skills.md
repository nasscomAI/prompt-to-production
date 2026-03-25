# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint row to determine its category, priority, reason, and review flag.
    input: A single citizen complaint row or description string.
    output: A structured object containing category, priority, reason, and flag fields.
    error_handling: If the description is genuinely ambiguous or unclassifiable, output category as 'Other' (or best guess) and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file.
    error_handling: If input file is missing, abort. If a row fails processing, log the error and continue with the next row.

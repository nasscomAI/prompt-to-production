# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority, reason, and any required review flags.
    input: A single citizen complaint description string.
    output: A structured object containing category (string), priority (string), reason (string), and flag (string).
    error_handling: Return a flag of NEEDS_REVIEW if the input is ambiguous or too poorly formatted to categorize.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, applies classification to each row, and writes the results to an output CSV.
    input: File paths for input CSV and output CSV.
    output: A written CSV file at the specified output path.
    error_handling: Log the error and skip the row if a row cannot be read properly, then continue to the next row.

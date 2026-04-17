# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single unstructured citizen complaint to strictly determine its category, priority, and justification.
    input: A single citizen complaint row/description string.
    output: A structured object containing the determined `category`, `priority`, a one-sentence `reason` citing specific words, and an optional ambiguity `flag`.
    error_handling: If the description is genuinely ambiguous and does not confidently map to an allowed category, it avoids false confidence by setting the `flag` to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Processes an input CSV file by systematically applying the classify_complaint skill to every row and writing to an output CSV.
    input: The file path to the input CSV containing raw citizen complaints.
    output: Writes the classification results to a target output CSV file, adding the required classification columns to each row.
    error_handling: If the input file is missing, it returns a file read error. For malformed rows within the CSV, it gracefully skips or logs a warning before continuing to the next row.

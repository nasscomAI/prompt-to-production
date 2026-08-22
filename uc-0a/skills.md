# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into structured categories and priorities.
    input: A single unstructured complaint string or row containing the complaint description.
    output: A structured record containing category, priority, reason, and flag fields.
    error_handling: If the complaint description is genuinely ambiguous or cannot be determined, outputs category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV file and writes the classified results to an output CSV file.
    input: Path to the input CSV file containing citizen complaints.
    output: Writes an output CSV file containing the classification results for each row.
    error_handling: Logs the error and continues processing the remaining rows if an input file is partially malformed.

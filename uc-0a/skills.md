# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: One complaint row.
    output: A structured output containing category, priority, reason, and flag.
    error_handling: Return category 'Other' and flag 'NEEDS_REVIEW' if the category is genuinely ambiguous or cannot be determined from the description.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint per row, and writes results to an output CSV file.
    input: The input file path and the output file path.
    output: A CSV file containing all processed complaint rows with classification fields added.
    error_handling: Must flag nulls, not crash on bad rows, and produce output even if some rows fail.

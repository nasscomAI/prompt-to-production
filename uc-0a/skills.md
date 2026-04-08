# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row to determine its category, priority, reason, and flag.
    input: One complaint row (text description of the complaint).
    output: A structure containing category, priority, reason, and flag.
    error_handling: If the input is genuinely ambiguous, return category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: A CSV file containing multiple citizen complaints.
    output: A CSV file containing the classifications (category, priority, reason, flag) for each input row.
    error_handling: Skip malformed rows or rows that fail to parse, logging an error message while continuing to process the rest of the batch.

# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a designated category, priority, reason, and flag.
    input: Single complaint row text.
    output: category, priority, reason, and flag strings.
    error_handling: If classification fails or is invalid, return category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: Input CSV path and output CSV path.
    output: A newly created output CSV file containing the classifications.
    error_handling: Skip or log rows that cannot be processed and continue with the remaining rows.

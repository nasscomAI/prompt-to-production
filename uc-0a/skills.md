skills:
  - name: classify_complaint
    description: Takes one citizen complaint row and classifies it into a category, priority, reason, and flag.
    input: A single string representing the complaint description from a CSV row.
    output: Four fields (category, priority, reason, flag) matching the strict taxonomy values.
    error_handling: If the text is genuinely ambiguous and cannot be matched, categorizes as 'Other' and sets the flag to 'NEEDS_REVIEW' instead of guessing.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes out a results CSV file.
    input: Path to an input CSV file containing raw complaint descriptions.
    output: A newly written CSV file containing the classifications aligned with the original rows.
    error_handling: If a row cannot be read, skips the invalid row and continues processing to ensure batch completion.

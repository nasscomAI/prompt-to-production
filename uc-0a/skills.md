# skills.md

skills:
  - name: classify_complaint
    description: Receives a single complaint row and determines the category, priority, reason, and flag based strictly on the text description.
    input: A single citizen complaint row containing a text description.
    output: Fields for category, priority, reason, and flag formatted for CSV writing.
    error_handling: If the text is genuinely ambiguous or cannot be determined, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV containing citizen complaints.
    output: File path to the generated output CSV containing the classified rows.
    error_handling: Handle file not found errors for the input and ensure unparseable rows do not halt the overall batch process.

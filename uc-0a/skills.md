# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint by determinining its category, priority, reason, and ambiguity flag.
    input: A single citizen complaint row containing a text description.
    output: A structured output containing exactly four fields - category, priority, reason, and flag.
    error_handling: If the input description is genuinely ambiguous or cannot be classified definitively, set category to "Other", priority based on keywords, and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the structured results to an output CSV.
    input: File path to the input CSV file containing citizen complaints.
    output: A new output CSV file with the original data plus the appended classification columns (category, priority, reason, flag).
    error_handling: If a row is malformed or cannot be parsed, log an error for that row and proceed to the next row without failing the entire batch process.

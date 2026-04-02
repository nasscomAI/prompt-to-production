# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, priority, reason, and flag.
    input: A single complaint row containing a description (string).
    output: Category (string from exact list), priority (Urgent, Standard, or Low), reason (one sentence citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If genuinely ambiguous or unclassifiable, output category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes the results to an output CSV.
    input: Path to an input CSV file containing complaint rows.
    output: A completed output CSV file containing the classifications.
    error_handling: Skips or flags malformed rows; halts and reports if file access or format errors occur.

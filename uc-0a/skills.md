# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, priority, reason, and an optional review flag.
    input: A single complaint row containing a description text.
    output: A record containing category (String), priority (String), reason (String), and flag (String).
    error_handling: If the complaint description is genuinely ambiguous, sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths to input CSV and output CSV.
    output: A newly written CSV file containing the classifications for all input complaints.
    error_handling: Skips processing or logs an error if the input CSV is unreadable.

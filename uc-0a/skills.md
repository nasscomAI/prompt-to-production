skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category and priority level with a justification and review flag.
    input: A single complaint description (string).
    output: A structured result containing category (exact string), priority (Urgent/Standard/Low), reason (one sentence citation), and flag (NEEDS_REVIEW or blank).
    error_handling: Sets the flag to NEEDS_REVIEW for ambiguous complaints and ensures categories follow the exact allowed taxonomy.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint logic to each row, and writes the results to an output CSV file.
    input: Input CSV file path containing 15 rows of citizen complaints.
    output: Output CSV file path containing classified results with category, priority, reason, and flag columns.
    error_handling: Validates file existence and ensures each row is processed according to the classification schema, handling missing or malformed data.

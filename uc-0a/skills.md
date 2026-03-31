skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority, reason, and flag.
    input: A single citizen complaint row/description (Text/String).
    output: Classified result containing category, priority, reason, and flag (Structured Object/JSON).
    error_handling: If the complaint is genuinely ambiguous, set the flag to 'NEEDS_REVIEW'. If no valid category fits, assign to 'Other'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint per row, and writes the final results to an output CSV.
    input: Path to the input CSV file containing citizen complaints.
    output: Path to the successfully generated output CSV file.
    error_handling: If the input file is missing or unreadable, halt and log an error. If a row is malformed, process as much as possible or output 'Other'/'NEEDS_REVIEW'.

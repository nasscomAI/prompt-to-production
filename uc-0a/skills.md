skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint text into strict schema fields (category, priority, reason, flag).
    input: A single text description representing the citizen complaint.
    output: A standardized record containing an exact-match category, priority (Urgent/Standard/Low), a one-sentence reason citing the text, and an optional flag.
    error_handling: If the complaint text is genuinely ambiguous and a specific category cannot be confidently assigned, set the flag field to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, applies classify_complaint to each row, and writes the structured results to an output CSV.
    input: File path to a valid input CSV containing citizen complaints.
    output: Writes a new output CSV file containing the classified rows.
    error_handling: If a row is malformed or processing fails, log the error and continue to the next row to ensure the rest of the batch completes. If the input file is missing, halt execution and throw an error.
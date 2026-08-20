skills:
  - name: classify_complaint
    description: Classifies a single complaint row into one exact category, assigns priority based on severity keywords, generates a reason citing words from the description, and sets a NEEDS_REVIEW flag when the category is genuinely ambiguous.
    input: A dict representing one CSV row with at least a 'description' field (string).
    output: Dict with keys — complaint_id (str), category (one of the 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing specific words from description), flag (NEEDS_REVIEW or blank string).
    error_handling: If description is empty or null, set category to Other, priority to Low, reason to 'No description provided', and flag to NEEDS_REVIEW. Never crash — always return a result dict.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the classified output.
    input: input_path (str) path to CSV file; output_path (str) path for results CSV.
    output: CSV file at output_path with columns complaint_id, category, priority, reason, flag — one row per input row.
    error_handling: If a row is malformed or classify_complaint raises an exception, write that row with category Other, priority Low, reason describing the error, and flag NEEDS_REVIEW. Never abort the batch — process all rows and report row-level errors in the reason field.

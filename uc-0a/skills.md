skills:
  - name: classify_complaint
    description: Classifies a single complaint's text description into a category and priority level, providing a citation and flagging ambiguity.
    input: A dictionary representing a single CSV row with keys like 'complaint_id' and 'description'.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty, category defaults to 'Other', priority to 'Standard', reason to 'Empty description provided.', and flag is set to 'NEEDS_REVIEW'. If ambiguous, flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: Input CSV path (string) and Output CSV path (string).
    output: Writes a CSV file containing columns: complaint_id, category, priority, reason, flag.
    error_handling: Logs and skips rows with parsing errors, ensuring the process completes even if individual rows fail.

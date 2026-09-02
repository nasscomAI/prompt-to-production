skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint into an approved category and priority with cited justification and ambiguity flagging.
    input: dict representing one complaint row, containing at least complaint_id (str) and description (str).
    output: dict with exact keys complaint_id (str), category (str), priority (str), reason (str), and flag (str).
    error_handling: If description is missing, empty, or unparseable, return category 'Other', priority 'Standard', reason 'Complaint description is missing or invalid.', and flag 'NEEDS_REVIEW'. If category is genuinely ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, executes classify_complaint for each record, and writes the structured classifications to an output CSV.
    input: input_path (str) pointing to source CSV file, and output_path (str) destination for the classified CSV file.
    output: Writes output CSV with header complaint_id,category,priority,reason,flag containing classification results for all input rows.
    error_handling: Handles malformed rows and parsing errors gracefully by catching exceptions per row, writing a fallback record with category 'Other' and flag 'NEEDS_REVIEW', ensuring batch execution does not crash and the output file is always written.

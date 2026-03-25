skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint describing an issue to determine its category, priority, justification (reason), and review flags, strictly following the defined operational boundary rules.
    input: A raw text string of the citizen complaint description.
    output: A structured object with exactly four fields - 'category' (chosen from the predefined list), 'priority' (Urgent, Standard, or Low), 'reason' (a single sentence justification quoting the text), and 'flag' (blank or 'NEEDS_REVIEW').
    error_handling: If the complaint is genuinely ambiguous, lacks sufficient detail, or falls outside explicit categories, it sets 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of citizen complaints from an input CSV file, applies the 'classify_complaint' skill to each row, and writes the structured classification results to an output CSV file.
    input: The file path to the input CSV file containing raw citizen complaints.
    output: The file path to the generated output CSV file containing the classifications ('category', 'priority', 'reason', and 'flag' columns) for each row.
    error_handling: Logs any row-level processing errors, marks problematic rows as failed or sets them to 'Other' with a 'NEEDS_REVIEW' flag, and continues progressing through the rest of the batch without crashing.

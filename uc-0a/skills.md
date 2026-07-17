skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description, returning category, priority, reason, and flag.
    input:
      type: dict
      format: "A dictionary with a 'description' key containing the complaint text, and optionally a 'complaint_id'."
    output:
      type: dict
      format: "A dictionary containing keys: complaint_id, category, priority, reason, flag."
    error_handling: >
      If description is missing, null, or empty, set category to 'Other', priority to 'Standard', reason to 'No description provided', and flag to 'NEEDS_REVIEW'. If the complaint is ambiguous, select the most likely category (or 'Other'), and set the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row, and writes the results to a CSV file.
    input:
      type: parameters
      format: "input_path: string (path to input CSV file), output_path: string (path to output CSV file)"
    output:
      type: None
      format: "Writes the classified records to the CSV file at output_path."
    error_handling: >
      Does not crash on bad rows or file read errors. If an input row lacks a description or is malformed, it flags the row with category: Other, priority: Standard, and flag: NEEDS_REVIEW, and continues processing the rest of the file.

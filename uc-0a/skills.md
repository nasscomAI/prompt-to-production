# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint text to determine its predefined category, priority level, justification, and whether it needs human review.
    input: A single string containing the text description of the complaint.
    output: A structured output (e.g. JSON or dictionary) containing exactly four fields - category (string from defined schema), priority (Urgent/Standard/Low), reason (single sentence citing exact words), and flag (NEEDS_REVIEW or empty).
    error_handling: If the category is ambiguous or cannot be confidently classified within the defined schema from the text alone, assigns the category "Other" and sets the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes an input CSV of citizen complaints by sequentially applying the classify_complaint skill to each row and writing the results to a new output CSV.
    input: A file path pointing to the input CSV file containing citizen complaints.
    output: A file path pointing to the generated output CSV file containing the original data appended with category, priority, reason, and flag columns.
    error_handling: Logs any errors encountered on specific rows (e.g. malformed data) without stopping the batch process, and gracefully outputs the processed rows.

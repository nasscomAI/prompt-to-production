skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, priority level, and reason, flagging it if ambiguous.
    input: A dictionary representing a single complaint row (keys include complaint_id, description, etc.).
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or null, set category to Other, priority to Low, reason to "Missing description", and flag to NEEDS_REVIEW. If the category is ambiguous or multiple categories overlap, select the primary category, set flag to NEEDS_REVIEW, and document this in the reason.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Input CSV file path (string) and output CSV file path (string).
    output: Writes a CSV file containing keys: complaint_id, category, priority, reason, flag.
    error_handling: Safe execution that flags nulls or empty descriptions, does not crash on corrupt/bad rows, and continues processing to ensure output is written even if some rows encounter issues.

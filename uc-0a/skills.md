skills:
  - name: classify_complaint
    description: Automatically categorizes a citizen complaint and assigns a priority level based solely on its textual description.
    input: A single string representing the raw text of the citizen complaint.
    output: A structured object convertible to CSV containing exactly four fields - category (string), priority (string), reason (string, one sentence), and flag (string or blank).
    error_handling: Handles ambiguity, completely incomprehensible text, or unrelated topics by setting category to "Other", leaving priority as "Low", explaining the refusal cleanly in the reason field, and setting flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the structured classification results to an output CSV file.
    input: File path to a CSV containing rows of raw citizen complaints.
    output: A generated CSV file perfectly aligning with the prescribed schema containing the appended category, priority, reason, and flag fields.
    error_handling: Logs any row that structurally fails to parse and gracefully skips it, ensuring continuous processing of the rest of the CSV.

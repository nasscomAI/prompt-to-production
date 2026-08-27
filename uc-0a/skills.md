- name: classify_complaint
  description: Categorizes a single citizen complaint description into a standardized category, priority severity, exact quoted reason, and ambiguity flag.
  input:
    type: string
    format: Raw text description of a single citizen complaint.
  output:
    type: object
    format: JSON structure containing string fields for category, priority, reason, and flag.
  error_handling: If the complaint category is genuinely ambiguous, sets the flag to NEEDS_REVIEW; rejects hallucinated or varying categories by enforcing exact taxonomy matches; prevents severity blindness by forcefully assigning Urgent priority if severity keywords are present; requires a missing justification to be filled with exactly one sentence quoted from the text.

- name: batch_classify
  description: Reads an input CSV of citizen complaints, sequentially applies the classifying skill to each row, and writes the complete results to an output CSV.
  input:
    type: file
    format: Filepath to an input CSV containing unclassified citizen complaint rows.
  output:
    type: file
    format: Filepath to an output CSV containing all original rows with newly appended classification columns.
  error_handling: If an individual row classification encounters schema validation errors or missing fields, logs the failure and proceeds to the next row to ensure the batch completes successfully.

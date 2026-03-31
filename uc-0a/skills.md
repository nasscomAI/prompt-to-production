skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into an exact predefined category and priority, providing a single-sentence justification and flagging ambiguity.
    input: String representing the description text of a single citizen complaint.
    output: A structured record containing exact string fields for category, priority, reason, and flag.
    error_handling: If the description is genuinely ambiguous, output category as "Other" and flag as "NEEDS_REVIEW" to prevent false confidence; enforce strict taxonomy strings to prevent hallucination and taxonomy drift; ensure reason is never missing to prevent missing justification.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iteratively applies the classify_complaint skill to each row, and writes all results to an output CSV.
    input: String path to the input CSV file containing multiple unclassified citizen complaints.
    output: String path to the newly written output CSV file containing the classifications.
    error_handling: If the input CSV file is malformed, missing, or unreadable, halt execution and raise an error; if individual rows are invalid, write them with appropriate error flags rather than failing the entire batch list.

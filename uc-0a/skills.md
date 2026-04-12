skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into a designated category and priority, citing reasons and flagging ambiguity.
    input: A single string or data object containing the citizen complaint description.
    output: A structured object with four fields - category (string, from predefined list), priority (string: Urgent, Standard, Low), reason (string, one sentence citing specific words), and flag (string, NEEDS_REVIEW or blank).
    error_handling: If description is completely uninterpretable, set category to "Other", priority to "Low", reason stating "Insufficient information", and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a batch of citizen complaints from an input CSV, processes each row using classify_complaint, and writes the classified records to an output CSV.
    input: A file path pointing to the input CSV file containing complaint rows.
    output: A file path pointing to the generated output CSV file containing the classifications.
    error_handling: If the input file is not found or has an unparseable structure, abort the batch process and return an error message indicating the file failure.

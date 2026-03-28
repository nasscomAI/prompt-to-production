# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description to assign a standardized category, determine priority level, provide a cited reason, and flag ambiguity.
    input: A single citizen complaint text description string.
    output: A structured record containing `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the complaint text is uninterpretable or missing key details, default category to 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, invokes classify_complaint for each row, and writes the structured results to an output CSV.
    input: File path to the input CSV containing citizen complaints.
    output: File path to the successfully generated output CSV file.
    error_handling: If a row fails to process due to parsing errors, write a default/error row or skip it, and continue processing the rest of the batch without crashing.

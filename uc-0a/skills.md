skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, and justification.
    input: A single complaint row containing a 'description' field.
    output: A dictionary or object containing category, priority, reason, and flag.
    error_handling: If the description is empty or completely unintelligible, categorize as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying the classification logic to each row and saving the results.
    input: Path to an input CSV file.
    output: Path to the generated output CSV file containing the new classification columns.
    error_handling: Reports any rows that could not be processed and ensures the output file structure is maintained even on partial failures.

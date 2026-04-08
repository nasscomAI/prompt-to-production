skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to classify it by category and assign a priority level based on severity keywords.
    input: A single citizen complaint text description string.
    output: A structured record containing string values for category, priority, reason, and flag.
    error_handling: Return category "Other" and set flag to "NEEDS_REVIEW" if the input text does not contain enough information to classify unambiguously.

  - name: batch_classify
    description: Reads an input CSV containing multiple citizen complaints, processes each row using the classify_complaint skill, and writes the results to an output CSV.
    input: The file path to an input CSV file containing citizen complaint descriptions without category and priority columns.
    output: The file path to the newly generated output CSV containing the required classification columns: category, priority, reason, and flag.
    error_handling: Skip rows that fail processing, logging an error indicating the row number, and continue to the next record.

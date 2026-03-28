skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint textual description and outputs categorized, prioritized, and justified structured data.
    input: A single unstructured complaint text string/row.
    output: A structured object/row containing exactly four fields - category, priority, reason, and flag.
    error_handling: If the input is completely unreadable or lacks detail, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, iterates over each row using classify_complaint, and writes the structured classification to an output CSV.
    input: A filepath to the input CSV and a filepath for the output CSV.
    output: A generated CSV file at the output path containing the classified categorizations.
    error_handling: Log errors for individually malformed rows and skip to the next row; abort cleanly if the input file goes missing or is profoundly corrupted.

skills:
  - name: classify_complaint
    description: Processes a single written complaint description to determine its category, priority, reason, and ambiguity flag without any hallucination.
    input: A single citizen complaint description string (zero-context text).
    output: A structured object with exactly four fields (category, priority, reason, flag) adhering to the strict schema.
    error_handling: If the complaint description is too ambiguous or missing information, sets category to 'Other' or standard categories and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, applies the classify_complaint skill per row, and writes the result out to an output CSV.
    input: File path to input CSV containing multiple rows of citizen complaint details.
    output: A new output CSV file containing the input rows alongside the newly classified columns (category, priority, reason, flag).
    error_handling: If a row fails to process, logs the error and continues to the next row, ensuring the batch continues to process as expected.

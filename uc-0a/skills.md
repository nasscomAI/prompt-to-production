skills:
  - name: classify_complaint
    description: Processes a single citizen complaint row to determine its category, priority, reason, and review flag based on strict schema rules.
    input: A single row containing a complaint description (String or Dictionary).
    output: A structured result with category, priority, reason, and flag fields (Dictionary or JSON).
    error_handling: If the complaint is too ambiguous to categorize, output category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a CSV file of complaints, iterates through them using classify_complaint, and writes the structured classifications to an output CSV file.
    input: Input CSV filepath (.csv).
    output: Output CSV filepath (.csv) containing original data plus classification columns.
    error_handling: If a row fails to parse or process, log the error and proceed to the next row to ensure batch completion.

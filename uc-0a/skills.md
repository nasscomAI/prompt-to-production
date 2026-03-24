skills:
  - name: classify_complaint
    description: Processes a single citizen complaint row and output its category, priority, reason, and review flag.
    input: A single complaint record containing the description text.
    output: A structured result containing category, priority, reason, and flag fields strictly following the schema.
    error_handling: If the input is invalid or genuinely ambiguous, outputs category "Other" and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, loops through applying the classify_complaint skill to each row, and writes the classifications to an output CSV file.
    input: File path to the input CSV and the desired output CSV path.
    output: A populated output CSV containing the results of the classification step (category, priority, reason, flag) for all rows.
    error_handling: Handles missing input files by aborting. If individual rows error out, defaults those rows to category "Other" with flag "NEEDS_REVIEW" and continues to the next row.

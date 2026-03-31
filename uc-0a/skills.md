skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag.
    input: A string of the complaint description.
    output: A JSON object with four exact keys - category, priority, reason, and flag.
    error_handling: Output category "Other" and flag "NEEDS_REVIEW" if the description is genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint per row, and writes to an output CSV.
    input: A string file path to the input CSV.
    output: A string file path to the newly written output CSV.
    error_handling: Log the problematic row ID, skip the row or output default Other/NEEDS_REVIEW, and continue processing.

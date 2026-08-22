

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, reason, and ambiguity flag.
    input: A single dictionary representing one row from the CSV containing at minimum a 'description' or 'complaint' text field.
    output: A dictionary containing five keys - complaint_id, category, priority, reason, flag.
    error_handling: If the input is missing the description text or is malformed, return category 'Other', priority 'Low', reason 'Malformed input row', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and output CSV.
    output: A newly created CSV file at the output path containing the classified data.
    error_handling: If the input file is not found or cannot be read, log the error and terminate safely. If a single row fails, log the error, output a fallback row with a NEEDS_REVIEW flag, and continue processing the rest of the batch.
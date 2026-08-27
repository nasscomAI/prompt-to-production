# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint to determine its category, priority, reason, and any required review flags.
    input: A single string or dictionary containing the raw complaint text description.
    output: A dictionary or object containing four fields (category, priority, reason, flag) matching the schema.
    error_handling: If the input is completely unparseable or ambiguous, output category as "Other" and set the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, and write the enriched records to an output CSV.
    input: File path to the input CSV file.
    output: A new CSV file saved to the specified output path containing all original columns plus the four classified columns.
    error_handling: Skip or safely handle malformed rows, log the error, and continue processing the rest of the file.

# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint to determine its category, priority, reason, and flag status based on RICE enforcement rules.
    input: A single complaint row containing a textual description (dict).
    output: A dictionary containing the required fields (category, priority, reason, and flag).
    error_handling: If input is completely unparseable, set flag to NEEDS_REVIEW and category to Other.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and output CSV (strings).
    output: A CSV file written to the output path containing classification results.
    error_handling: Must not crash on bad rows. If a row fails to process, write default/null values with a flag and continue processing the rest. Produce an output file even if some rows fail.

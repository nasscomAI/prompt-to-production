skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on predefined rules.
    input: Dictionary containing a single complaint row (including the description).
    output: Dictionary containing the original row data plus the newly assigned category, priority, reason, and flag.
    error_handling: If the category is ambiguous or cannot be determined from the description alone, output category 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: String path to the input CSV file and String path to the output CSV file.
    output: An output CSV file written to the specified path containing all classified complaints.
    error_handling: Must flag nulls or bad rows without crashing, and produce an output file even if some rows fail processing.

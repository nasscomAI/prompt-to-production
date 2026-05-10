skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category, priority, reason, and flag.
    input: A dictionary representing a single complaint row.
    output: A dictionary containing the classification results with keys category, priority, reason, and flag.
    error_handling: If the input is invalid, ambiguous, or cannot be categorized, it assigns the category 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string) and output_path (string).
    output: Writes the results to the specified output CSV file.
    error_handling: Flags nulls, does not crash on bad rows, and produces output even if some individual rows fail to classify.

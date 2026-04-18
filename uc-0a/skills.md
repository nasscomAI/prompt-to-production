skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and reason, flagging it if ambiguous.
    input: A dictionary containing the complaint details, specifically the 'description' field as a string.
    output: A dictionary containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string, either 'NEEDS_REVIEW' or empty).
    error_handling: If the input description is missing or empty, returns 'Other', 'Low', 'No description provided.', and 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of multiple complaints, applies classify_complaint to each row, and writes the results to a new CSV.
    input: input_path (string) for the source CSV and output_path (string) for the destination CSV.
    output: Writes a CSV file to the output_path. Returns nothing.
    error_handling: If a row fails to parse, logs the error and continues. Flags null descriptions as 'NEEDS_REVIEW'.

skills:
  - name: classify_complaint
    description: Processes a single complaint row and outputs its category, priority, reason, and flag.
    input: A single string containing the complaint description.
    output: A structured record containing `category`, `priority`, `reason`, and `flag`.
    error_handling: If the complaint description is too ambiguous or missing key details to confidently categorize, set the `flag` field to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Path to the input CSV file.
    output: Writes processed rows to the specified output CSV file path.
    error_handling: If a row fails to process or classify cleanly, log the error for that row and continue processing the rest, marking the failed row's flag as NEEDS_REVIEW if possible.

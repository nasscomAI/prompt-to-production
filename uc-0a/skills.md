skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint text and outputs its classification category, priority, reason, and an ambiguity flag if needed.
    input: A string of a single row/complaint from the input CSV.
    output: A JSON object containing 'category', 'priority', 'reason', and optionally 'flag'.
    error_handling: Return category="Other", flag="NEEDS_REVIEW", and priority="Standard" if input is unparsable or completely ambiguous.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies the classify_complaint skill row by row, and writes the output back to an output CSV.
    input: File paths for the input CSV and the output CSV.
    output: A summary confirming the completion of the batch process and output file write.
    error_handling: Return an error message indicating that the input CSV could not be read.

# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and maps it to a standard category and priority.
    input: A string containing the unstructured citizen complaint description.
    output: A dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Returns category as 'Other' and sets flag to 'NEEDS_REVIEW' if the text is unparseable or ambiguous.

  - name: batch_classify
    description: Reads a CSV file of complaints, iteratively applies classify_complaint to each row, and writes the structured results to an output CSV.
    input: File paths to the input CSV and the intended output CSV.
    output: A boolean indicating success, and writes a newly formatted CSV to disk.
    error_handling: Skips malformed rows silently and securely closes output files even if partial failure occurs.

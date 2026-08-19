# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes one raw complaint and maps it to the Municipal Classification Schema.
    input: Dictionary with 'complaint_id' and 'description'.
    output: Dictionary with 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Map unrecognized complaints to 'Other' with a 'NEEDS_REVIEW' flag.

  - name: batch_classify
    description: Processes a collection of complaints from a CSV file and writes to an output CSV.
    input: Paths for input CSV and output results CSV.
    output: A completed CSV following the fixed schema columns.
    error_handling: Log errors for missing input rows or null values without stopping the process.

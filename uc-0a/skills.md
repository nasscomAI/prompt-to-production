# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and reason for classification.
    input: A dictionary representing a row from the input CSV, containing at least 'complaint_id' and 'description'.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If 'description' is missing or empty, returns category 'Other', priority 'Standard', reason 'Missing description', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and saves the results to a new CSV file.
    input: Paths to the input CSV file and the desired output CSV file.
    output: None (writes to a file).
    error_handling: Handles missing input files gracefully and ensures the output file is created even if some rows fail to classify.

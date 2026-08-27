skills:
  - name: classify_complaint
    description: Classify a single complaint row into a standardized category, priority, reason, and an optional review flag.
    input: A single dictionary representing one complaint row containing at least a 'description' or text of the complaint.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW', and a reason explaining the ambiguity if the description is invalid, empty, or unclassifiable.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: File path to the input CSV (string) and file path to the output CSV (string).
    output: Writes a CSV file to the output path; returns nothing or a success status.
    error_handling: Flag null rows, do not crash on bad rows, skip/log errors for invalid rows, and produce the output file even if some rows fail.

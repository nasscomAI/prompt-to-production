# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single raw complaint into a structured category and priority format.
    input: A dictionary/row representing a single complaint containing a 'description'.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If classification fails or is ambiguous, outputs category 'Other' with flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints and generates a categorized results Excel (.xlsx) file.
    input: File paths for target input CSV and destination output .xlsx.
    output: Writes an Excel file to output_path containing strictly four columns (Category, Priority, Reason, Flag).
    error_handling: Catches individual row exceptions to ensure completion; logs errors in Reason field and flags 'NEEDS_REVIEW'.

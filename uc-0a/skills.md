skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint record to determine its category and priority.
    input: dictionary containing complaint details (description, location, etc.)
    output: dictionary containing keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'
    error_handling: Return category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', and a generic reason if parsing fails or input is null.

  - name: batch_classify
    description: Reads complaints from a CSV, processes them row by row securely, and writes the classified output to a new CSV.
    input: file path to input CSV and file path to output CSV
    output: none (writes a file)
    error_handling: Skips completely malformed rows with missing IDs but continues processing the rest without crashing.

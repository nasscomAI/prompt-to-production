skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category, priority, justification, and review status.
    input: A dictionary representing a single complaint row.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Returns category "Other", flag "NEEDS_REVIEW", and a stated reason if the input description is missing, invalid, or completely ambiguous.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string path to input CSV) and output_path (string path to output CSV).
    output: Writes a CSV file containing the classifications for all rows.
    error_handling: Flags null rows, catches errors on malformed rows without crashing the process, and produces the output CSV for all successfully processed rows.

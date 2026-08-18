# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category and priority, citing a reason and setting a flag if ambiguous.
    input: A string representation of the complaint description.
    output: A JSON object with keys `category`, `priority`, `reason`, and `flag`.
    error_handling: Return a JSON with category 'Other', priority 'Standard', reason 'Error parsing complaint', flag 'NEEDS_REVIEW' if input is invalid or ambiguous.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for input CSV and output CSV.
    output: A newly created CSV file with the added classification columns.
    error_handling: Must flag nulls, skip bad rows without crashing, and produce an output file even if some rows fail.

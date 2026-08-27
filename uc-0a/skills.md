# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to deduce its category, priority, reason, and any required flags.
    input: A single citizen complaint row containing description text.
    output: A row with classification fields (category, priority, reason, flag).
    error_handling: If the complaint is highly ambiguous or cannot be classified, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes the results to an output CSV.
    input: Filepath to the input CSV containing complaints.
    output: Filepath to the output CSV containing classified results.
    error_handling: Log row-level classification errors and continue processing the rest of the file. Halts only if the input file cannot be read or output file cannot be written.

# skills.md

skills:
  - name: classify_complaint
    description: Parses a single citizen complaint description and categorizes it based on a strict predefined schema.
    input: A single citizen complaint row/description (Text).
    output: Returns four fields - category (String), priority (String), reason (String of 1 sentence), and flag (String).
    error_handling: If the complaint description is ambiguous, it returns 'Other' or leaves the category blank, and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, iteratively applies classify_complaint to each row, and writes the results.
    input: File path to the input CSV containing rows of citizen complaints.
    output: Writes an output CSV file with the classified category, priority, reason, and flag columns appended.
    error_handling: Invalid rows are skipped or logged, and if an output file cannot be written, an error is reported to the user.

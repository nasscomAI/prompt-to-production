# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its standard category, priority, reason, and any flags.
    input: A single complaint row containing descriptions or relevant details (Text or Dictionary).
    output: A structure containing category (exact string match), priority (Urgent, Standard, Low), reason (one sentence citing specific words), and flag (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is genuinely ambiguous, assigns Other to the category and sets flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint sequentially to each row, and writes the results to an output CSV.
    input: Filepath to the input CSV and filepath to the output CSV.
    output: A generated CSV file at the specified output path with newly classified columns.
    error_handling: If a row fails classification, gracefully handles the error, sets flag to NEEDS_REVIEW, and continues to the next row to ensure output file is successfully created with correct row count.

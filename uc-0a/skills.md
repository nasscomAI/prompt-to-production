# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, priority, reason, and an optional review flag.
    input: A single citizen complaint record containing the description text (Dictionary or String).
    output: A dictionary/object containing `category` (String), `priority` (String), `reason` (String), and `flag` (String/blank).
    error_handling: If the complaint description is ambiguous or the category cannot be confidently determined, sets the category to 'Other' (or the closest match) and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, processes each row using classify_complaint, and writes the results to an output CSV.
    input: Filepath to the input CSV file containing citizen complaints (String).
    output: Writes an output CSV file with the classifications and returns a success status or the output filepath (String).
    error_handling: If a row is malformed or throws an exception during processing, catches the error, sets default values with a 'NEEDS_REVIEW' flag, and continues to the next row.

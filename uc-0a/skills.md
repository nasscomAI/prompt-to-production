# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority, and a supporting reason based on a strict classification schema.
    input: String containing the complaint description.
    output: Object containing `category` (string), `priority` (Urgent/Standard/Low), `reason` (single sentence citation), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the description is ambiguous or doesn't match a specific category, set `category: Other` and `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV file, applies the `classify_complaint` skill to each row, and writes the results to a specified output CSV file.
    input: File path to the input CSV and file path for the output CSV.
    output: Success confirmation and the path to the generated output CSV.
    error_handling: Log errors for rows with missing descriptions or invalid formats, ensuring the process continues for the rest of the file.


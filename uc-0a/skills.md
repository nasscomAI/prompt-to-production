# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, assigns a priority, provides a reason, and adds a flag if ambiguous.
    input: A single complaint row (e.g., text description and any other provided fields) in string or dictionary format.
    output: A dictionary containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the category cannot be determined, it outputs category "Other" and sets the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV containing multiple complaint rows, processes each row using classify_complaint, and writes the results to an output CSV.
    input: File path to the input CSV file.
    output: File path to the generated output CSV file.
    error_handling: Skips rows with entirely missing or malformed data, logs the error, and continues processing the rest of the file.

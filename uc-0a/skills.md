# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single raw complaint description into its designated category and severity priority.
    input: A string containing the complaint description text.
    output: A JSON object with the keys `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the input description is completely unreadable or missing, set the category to "Other", priority to "Low", reason to "Invalid input description provided", and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row individually using `classify_complaint`, and writes the structured results to another CSV file.
    input: An input file path (string) and an output file path (string).
    output: A new CSV file saved at the output file path containing all original data columns along with the new classification columns.
    error_handling: It must handle API rate limits gracefully with retries, skip or flag badly formatted rows without crashing the script, and guarantee that an output file is produced even if some rows fail.

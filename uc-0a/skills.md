skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, reason, and flag based on the provided schema.
    input: A single citizen complaint row/string containing the complaint description.
    output: A structured object (e.g., dictionary) containing `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the category is ambiguous or cannot be determined from the description alone, outputs category as "Other" and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the complete results to an output CSV file.
    input: A file path to the input CSV file.
    output: An output CSV file path where the results have been written.
    error_handling: Raises an error if the input file is not found or unreadable. If an individual row is malformed, it should either attempt to classify it as "Other"/"NEEDS_REVIEW" or log the error and proceed to the next row.

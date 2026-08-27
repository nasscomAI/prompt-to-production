# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and returns its taxonomy classification.
    input: A single string representing the citizen complaint description.
    output: A structured record containing `category` (string), `priority` (string), `reason` (string), and `flag` (string, either "NEEDS_REVIEW" or blank).
    error_handling: Return category "Other" and set flag to "NEEDS_REVIEW" if the description is totally ambiguous or unintelligible.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the structured classification to an output CSV.
    input: File path to the input CSV file.
    output: A new output CSV file containing the original rows with the predicted `category`, `priority`, `reason`, and `flag` columns appended.
    error_handling: If an individual row fails to process, log the error, populate default values with "NEEDS_REVIEW" flag, and continue processing the rest of the file.

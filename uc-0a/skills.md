# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a standardized category, priority level, extraction reason, and ambiguity flag.
    input: A string or JSON object containing the complaint description text.
    output: A structured object containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the text is completely ambiguous or unreadable, output category: 'Other', flag: 'NEEDS_REVIEW', and a default low/standard priority.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies the classify_complaint skill to every row, and writes the structured results to an output CSV.
    input: File path to the input CSV and file path to the output CSV.
    output: A successfully written output CSV file and a completion status.
    error_handling: If a row fails to process due to malformed data, log the error and continue to the next row without halting the entire batch process.

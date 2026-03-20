skills:
  - name: classify_complaint
    description: Classifies a single raw citizen complaint row into a category, priority, reason, and flag.
    input: A single row of complaint text (string).
    output: A JSON object containing keys "category" (string), "priority" (string), "reason" (string), and "flag" (string).
    error_handling: If the text is empty or classification fails entirely, set category: Other, priority: Low, reason: "Invalid input", flag: "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a batch of complaints from a CSV, applies classify_complaint to each row, and writes the output back to a CSV.
    input: File paths to the input CSV and output CSV.
    output: A newly generated CSV file at the specified output path containing the classified data.
    error_handling: Skip invalid rows and log an error line in the output or flag the row if it cannot be parsed.

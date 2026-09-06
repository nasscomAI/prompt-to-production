skills:
  - name: classify_complaint
    description: Classifies one citizen complaint using the approved category and priority rules.
    input: "A dictionary representing one CSV row, containing a non-empty description string."
    output: "A dictionary containing category, priority, reason, and flag."
    error_handling: "Reject missing or empty descriptions; use only approved category values; set priority to Urgent when a severity keyword appears; set flag to NEEDS_REVIEW when the category is genuinely ambiguous; never invent a sub-category."

  - name: batch_classify
    description: Reads complaints from a CSV file, classifies every row, and writes the completed results to another CSV file.
    input: "A UTF-8 CSV file path containing complaint rows with a description column."
    output: "A UTF-8 CSV file containing the original columns plus category, priority, reason, and flag."
    error_handling: "Stop with a clear error when the input file cannot be read or the description column is missing; preserve row order; apply classify_complaint to every valid row; mark ambiguous complaints for review instead of guessing."

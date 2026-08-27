skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row to determine its category, priority, reason, and an optional review flag.
    input: A single citizen complaint description or row data.
    output: A structured object containing `category`, `priority`, `reason`, and `flag` fields.
    error_handling: If the description is genuinely ambiguous, it sets category as "Other" (or most likely category) but strictly outputs "NEEDS_REVIEW" in the flag field.

  - name: batch_classify
    description: Reads an input CSV file of complaints, iterates over each row applying classify_complaint, and writes the complete results to an output CSV.
    input: The file path to the input CSV containing citizen complaints.
    output: Produces a new CSV file (e.g., results_[city].csv) encompassing the classified category, priority, reason, and flag for each row.
    error_handling: Logs any processing issues for individual rows and continues execution; fails gracefully with an error if the input file is unreadable or not found.

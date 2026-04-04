# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its exact category, priority based on severity keywords, a specific quoted reason, and any required review flags.
    input: A single complaint containing its textual description.
    output: A structured record containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is genuinely ambiguous or does not fit standard constraints, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row individually, and writes the combined output to a new CSV file.
    input: File paths for an input CSV and the desired output CSV.
    output: A populated output CSV file containing the classifications for every input row.
    error_handling: If a row throws an unhandled error during classification, log the error and record the row with a 'PROCESSING_ERROR' flag to prevent pipeline failure.

# skills.md

skills:
  - name: classify_complaint
    description: Receives a single complaint row and determines its standardized category, priority, reason, and flag according to the RICE rules.
    input: A dictionary containing the raw complaint data (keys like 'description', 'complaint_id').
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing or null, output category 'Other' and flag 'NEEDS_REVIEW'. If ambiguous, fall back to 'Other' with 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the augmented data to an output CSV.
    input: Two strings representing the file paths for the input CSV and output CSV.
    output: Writes parsed and classified rows to the output CSV file and returns nothing.
    error_handling: Must not crash on bad rows or missing fields. If a row fails to process normally, flag it as 'NEEDS_REVIEW' and continue to the next row, ensuring it still writes out to the output file.

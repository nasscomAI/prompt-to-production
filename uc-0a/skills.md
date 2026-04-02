21222222# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to extract its category, priority, justification reason, and any required review flags.
    input: A single citizen complaint description string or data row.
    output: A structured record containing exactly four fields (category, priority, reason, flag) adhering to the classification schema.
    error_handling: If the complaint description is vague, missing, or cannot be confidently classified, determine the best guess category, or 'Other', and set the flag to 'NEEDS_REVIEW'. Do not exhibit false confidence.

  - name: batch_classify
    description: Processes a CSV file of complaints by applying the classify_complaint skill to each row and writing the combined results to an output CSV.
    input: A file path to an input CSV containing multiple rows of citizen complaints (e.g. 15 rows where category/priority are stripped).
    output: A file path to a generated output CSV file containing the classifications for all processed rows.
    error_handling: If a row fails entirely, ensure the row in the output CSV still exists but with the flag 'NEEDS_REVIEW' and a relevant error reason, without halting the entire batch process.

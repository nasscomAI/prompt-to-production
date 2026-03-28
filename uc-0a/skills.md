# skills.md

skills:
  - name: classify_complaint
    description: Processes a single text description of a citizen complaint to extract and assign its appropriate classification fields.
    input: A single string representing one row's complaint description from the input CSV.
    output: A structured record containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string or blank).
    error_handling: If the input is fundamentally ambiguous or context is missing, set category to 'Other', priority to 'Low', flag to 'NEEDS_REVIEW', and clearly state the ambiguity in the reason field.

  - name: batch_classify
    description: Reads an input CSV file of civic complaints, iterates over each row using classify_complaint, and writes the structured output to a new CSV.
    input: Two file path strings representing the source CSV file and the destination CSV file.
    output: An exported CSV file containing the original rows appended with the newly classified category, priority, reason, and flag columns.
    error_handling: If individual rows fail, append them with flag 'NEEDS_REVIEW' and log the error, but do not halt the entire batch execution.

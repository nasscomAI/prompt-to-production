# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single raw complaint description into a predefined category and priority, with a reason and review flag.
    input: A string representing a single complaint description.
    output: A JSON dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: Refuses to output invalid categories. If input is completely unparseable or irrelevant, returns category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of city complaints, applies classify_complaint to each row's description, and writes the results including the new classification columns to an output CSV.
    input: An input CSV filepath (string) and an output CSV filepath (string).
    output: Returns nothing. Writes a new output CSV appending specific inferred columns (category, priority, reason, flag) to the original data.
    error_handling: Handles malformed rows or model API errors gracefully by recording the fields as blank or flagging them, ensuring the process does not crash on a bad row.

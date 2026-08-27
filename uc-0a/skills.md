# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a specific category, priority, reason, and flag based on the description text.
    input: A dictionary containing the complaint data (e.g., complaint_id, description, location).
    output: A dictionary containing the classified fields (complaint_id, category, priority, reason, flag).
    error_handling: If input lacks a description, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, classifies each row, and writes the results to a new CSV file.
    input: Two strings representing the input CSV path and the output CSV path.
    output: Writes a CSV file and returns None.
    error_handling: Flags missing fields, does not crash on malformed rows, and ensures output is written even if some rows fail.

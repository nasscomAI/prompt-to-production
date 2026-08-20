# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into structured fields.
    input: String containing the complaint 'description'.
    output: JSON object containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Return a default 'Other' category fallback if classification fails.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each, and writes the results to an output CSV.
    input: File paths for input CSV and output CSV.
    output: Writes CSV to file system.
    error_handling: Ignore and skip rows that fail parsing to ensure batch process completes.

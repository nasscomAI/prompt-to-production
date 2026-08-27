# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: summarize_policy
    description: Reads a policy document and generates a summary that preserves all numbered clauses without changing meaning or omitting conditions.
    input: File path to the policy text document (string).
    output: Summary text string containing all clauses, or writes to an output file.
    error_handling: If the input file is not found or unreadable, reports the error and does not produce output.

# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text and return a structured mapping of numbered clauses to their text.
    input: Path string to `policy_hr_leave.txt`.
    output: Dictionary mapping clause numbers like `2.3` to clause text.
    error_handling: If the file is missing or malformed, raise a clear error and do not produce a summary.

  - name: summarize_policy
    description: Create a compliant summary of required clauses using the structured policy sections.
    input: Dictionary of numbered clauses and a list of required clause numbers.
    output: A text summary with clause references and clause text or verbatim quotes where needed.
    error_handling: If a required clause is missing, include a note that the clause text was unavailable in the source document.

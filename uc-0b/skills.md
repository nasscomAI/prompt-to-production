# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured representation of the policy document with distinct numbered sections (JSON/dictionary).
    error_handling: Return a descriptive error if the file is not found, unreadable, or missing numbered sections.

  - name: summarize_policy
    description: Produces a strictly compliant summary from structured sections, preserving all clauses and conditions.
    input: Structured policy sections (JSON/dictionary).
    output: A condensed summary text ensuring all multi-condition obligations and original clause references are retained (string).
    error_handling: Return an error if the input format is invalid or if clauses cannot be extracted properly.

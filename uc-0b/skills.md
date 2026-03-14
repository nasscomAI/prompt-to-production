# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a local .txt policy file and returns its content as structured text.
    input: File path string pointing to the policy document.
    output: Raw string containing the full text of the policy document.
    error_handling: If the file is not found or cannot be read, throws an exception and halts execution.

  - name: summarize_policy
    description: Takes the raw policy text and produces a compliant summary focusing on specific clauses without dropping conditions.
    input: Raw text of the policy document.
    output: Formatted string containing the bulleted summary of the 10 core clauses.
    error_handling: If a clause cannot be parsed or safely condensed, quotes the clause verbatim and appends a [NEEDS_REVIEW] flag.

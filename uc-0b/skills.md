# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a text policy file and returns the content parsed into structured numbered sections.
    input: File path (string).
    output: Structured representation of clauses (e.g., JSON list of objects).
    error_handling: Return error message if file path is invalid or file is unreadable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured sections (list/object).
    output: Summarized text (string) referencing original clauses.
    error_handling: If unable to summarize without losing meaning, flag the issue and output the clause verbatim.

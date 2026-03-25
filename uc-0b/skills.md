skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document (string).
    output: Structured representation of the policy document with numbered sections and text.
    error_handling: Return an error if the file cannot be found, cannot be read, or cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input: Structured policy sections (output from retrieve_policy).
    output: A summarised text document maintaining all clauses and conditions with accurate clause references.
    error_handling: If input sections are invalid or missing, fail the summarization and return an error detailing the missing structure.

# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Filepath string pointing to the policy .txt file.
    output: A structured mapping (e.g., dictionary) of clause numbers to their text.
    error_handling: If the file is missing or cannot be read, throws an error or returns an empty structure to prevent partial processing.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with explicit clause references.
    input: Structured numbered sections (from retrieve_policy).
    output: A summarized text string containing all clauses and their precise obligations.
    error_handling: If a clause cannot be summarized without meaning loss, quotes it verbatim and adds a flag for manual review.
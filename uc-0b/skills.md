skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: The file path to the .txt policy document (string).
    output: A list or dictionary of structured numbered sections containing the text of each clause.
    error_handling: If the file is not found or cannot be read, it returns an error and stops execution.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: A list or dictionary of structured numbered sections.
    output: A string containing the compliant summary with appropriate clause references.
    error_handling: If a clause cannot be summarized without meaning loss, quotes it verbatim and flags it.

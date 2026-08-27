skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: String representing the file path to the .txt policy document.
    output: Dictionary or structured list containing the numbered clauses and text.
    error_handling: If the file is missing or unreadable, raise a FileNotFoundError and print an error message.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, ensuring no conditions are dropped.
    input: Dictionary or structured list of text sections.
    output: String containing the formatted summary.
    error_handling: If a clause is ambiguous or too complex to summarize safely, quote it verbatim and add a [NEEDS_REVIEW] or [VERBATIM] flag to prevent meaning loss.
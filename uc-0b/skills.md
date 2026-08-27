# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as parsed, structured numbered sections and clauses.
    input: A string representing the file path of the .txt policy document.
    output: A dictionary or structured list mapping clause numbers to their exact text.
    error_handling: Raises an explicit FileNotFoundError if the document is missing or unreadable, returning a safe fallback error message.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant, strict summary preserving all obligations and conditions.
    input: The structured sections/clauses (dictionary or list) outputted by retrieve_policy.
    output: A formatted string containing the compliant summary with explicit clause references.
    error_handling: Flags any clause that fails processing or appears contradictory with a '[NEEDS_REVIEW]' tag in the output rather than omitting it.

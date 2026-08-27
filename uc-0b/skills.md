skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into a dictionary of section numbers mapped to their raw text content.
    input: String path to the policy text file.
    output: Dictionary mapping clause numbers (e.g., '2.3') to their corresponding text strings.
    error_handling: Raises FileNotFoundError if the path is invalid.

  - name: summarize_policy
    description: Condenses parsed policy clauses into a summary while preserving all conditions, adding verbatim text.
    input: Dictionary mapping clause numbers to text strings.
    output: String summary containing clause summaries and verbatim quotes.
    error_handling: Fallbacks to printing the verbatim clause if a summary cannot be constructed without meaning loss.

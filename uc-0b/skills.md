skills:
  - name: retrieve_policy
    description: "Load the policy .txt file and return its content structured by numbered sections/clauses."
    input: "The file path (string) of the policy document."
    output: "A dictionary mapping clause numbers (e.g. '2.3') to their full text content."
    error_handling: "If the file is missing or unreadable, raise a FileNotFoundError."

  - name: summarize_policy
    description: "Summarize the structured policy sections into a compliant format, citing clause references."
    input: "A dictionary of structured clauses."
    output: "A formatted summary string containing every numbered clause, preserving all conditions."
    error_handling: "If a clause is missing or cannot be parsed, include a placeholder and flag it as NEEDS_REVIEW."

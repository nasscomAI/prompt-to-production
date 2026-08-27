skills:
  - name: retrieve_policy
    description: Load the .txt policy file and return its content as structured, numbered sections.
    input: File path of the policy document (string).
    output: A dictionary mapping clause numbers (e.g. "2.3") to their raw text content (string).
    error_handling: Raise FileNotFoundError if the file doesn't exist, and return an empty dictionary if parsing fails.

  - name: summarize_policy
    description: Take the structured policy clauses and produce a compliant summary text preserving all obligations, conditions, and binding verbs exactly.
    input: A dictionary of structured clauses.
    output: A summarized text document (string).
    error_handling: If a clause is missing from the input, explicitly output a placeholder indicating the clause was missing from the source.

# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content clearly structured by numbered sections and clauses.
    input: File path to the policy .txt file (string).
    output: A dictionary mapping numbered clauses to their raw text content.
    error_handling: Raise an error if the file cannot be read or if no recognizable numbered clauses are found.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary that perfectly preserves multi-condition obligations.
    input: Structured policy sections (dictionary).
    output: A string containing the formatted summary referencing all the original numbered clauses.
    error_handling: If a clause cannot be confidently shortened without losing specific conditions, output it verbatim with a [VERBATIM] tag.

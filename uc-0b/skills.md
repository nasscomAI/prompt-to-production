# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections and numbered clauses.
    input: A file path (string) pointing to the policy document (.txt).
    output: A dictionary mapping clause numbers to their exact text content.
    error_handling: If the file is unreadable or malformed, return an error message and halt execution.

  - name: summarize_policy
    description: Takes the structured clauses and generates a compliant summary that strictly preserves all conditions and meaning.
    input: A dictionary of structured clauses.
    output: A string containing the compliant summary, with explicit clause references.
    error_handling: If a clause cannot be confidently summarized without dropping conditions, quote it verbatim and flag it.

# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy file (.txt) and returns its content as a list of structured numbered sections.
    input: File path (string) to the .txt policy document.
    output: List of structured sections (e.g., { "clause": "2.3", "text": "..." }).
    error_handling: Raise error if file is missing, unreadable, or contains no identifiable numbered clauses.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that preserves all conditions and clause references.
    input: List of structured policy sections.
    output: Markdown summary containing all original clause numbers and preserved obligations.
    error_handling: Return error if input list is empty or if clauses are missing key obligations.

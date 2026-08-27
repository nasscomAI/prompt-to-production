# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to a .txt policy document.
    output: A list of dictionaries or a structured object containing clause numbers and their text.
    error_handling: Raises FileNotFoundError if the file is missing; returns an empty list if no numbered clauses are found.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, ensuring no meaning loss.
    input: Structured policy sections (list of clauses).
    output: A string summary where every numbered clause is present and conditions are preserved.
    error_handling: Flags clauses that cannot be summarized without meaning loss for verbatim inclusion.

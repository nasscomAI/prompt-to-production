skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content parsed as structured numbered sections.
    input: file_path (str)
    output: dict (mapping section numbers to their text content)
    error_handling: Raises an error if the file is missing; returns an empty dictionary if the format is unrecognizable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clauses, conditions, and obligations with exact clause references.
    input: dict (structured sections)
    output: str (formatted summary text)
    error_handling: Quotes the clause verbatim and adds a flag if a clause cannot be safely summarized without losing its meaning or conditions.

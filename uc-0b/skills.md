# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: The complete content of the text file (string).
    error_handling: Return a descriptive error if the file is missing or cannot be read.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured policy text (string).
    output: A summary text mapped to clauses, capturing all conditions (string).
    error_handling: If the input lacks numbered clauses, summarize verbatim and add a warning flag.

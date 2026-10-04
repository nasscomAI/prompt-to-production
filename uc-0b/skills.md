# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) to a plain-text policy document.
    output: List of dictionaries, each with "section_heading" (str), "clause_id" (str), and "clause_text" (str).
    error_handling: Raises FileNotFoundError if the path does not exist. Raises ValueError if the file does not contain numbered clauses matching the expected pattern.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with clause references.
    input: List of dictionaries (structured sections from retrieve_policy).
    output: Plain-text summary string where every numbered clause is represented with its core obligation and original binding verb, multi-condition obligations are fully preserved, and no information outside the input is added.
    error_handling: Raises ValueError if any clause_id is missing a core obligation or binding verb. Flags clauses that cannot be summarised without meaning loss with '[VERBATIM]' rather than guessing.

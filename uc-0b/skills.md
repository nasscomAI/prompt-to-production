# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections with clause references.
    input: File path to a .txt policy document.
    output: List of dictionaries, each with keys: section_number, clause_number, content, binding_verb.
    error_handling: If file is missing or empty, raise descriptive error. If section structure is malformed, return raw text with warning.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all clause obligations and conditions.
    input: List of structured section dictionaries from retrieve_policy.
    output: String containing the summary with clause references and any [VERBATIM] flags for complex clauses.
    error_handling: If input sections are empty, return error message. If a clause cannot be summarized without loss, include verbatim quote with flag.
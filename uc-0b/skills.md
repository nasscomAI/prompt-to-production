# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content structured by numbered sections.
    input: file_path (string)
    output: dictionary of {clause_number: text_content}
    error_handling: Return "File Not Found" or "Invalid Format" if the structure cannot be parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a summary that adheres to enforcement rules.
    input: structured_clauses (dict)
    output: markdown string with preserved obligations and clause references.
    error_handling: Flag sections that cannot be summarized without losing mandatory conditions.

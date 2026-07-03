skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured numbered sections.
    input:
      type: string
      format: "path to a .txt policy file"
    output:
      type: object
      format: "dictionary with section numbers as keys and section content as values"
    error_handling:
      invalid_input: "Return an empty dictionary and an error message indicating the file could not be read or is not a valid text file."
      ambiguous_input: "Not applicable as input is a file path."
      failure_modes:
        - "Refuse to process if the input file path is invalid or inaccessible."
  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references.
    input:
      type: object
      format: "dictionary with section numbers as keys and section content as values"
    output:
      type: string
      format: "A summary of the policy with all numbered clauses, their conditions, and original clause references. If a clause cannot be summarized without meaning loss, it will be quoted verbatim and flagged."
    error_handling:
      invalid_input: "Return an error message indicating that the input structured sections are invalid or empty."
      ambiguous_input: "If a clause is genuinely ambiguous and cannot be summarized without meaning loss, quote it verbatim and flag it."
      failure_modes:
        - "Every numbered clause must be present in the summary."
        - "Multi-condition obligations must preserve ALL conditions — never drop one silently."
        - "Never add information not present in the source document."
        - "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it."
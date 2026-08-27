skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections to prevent omission of any clause.
    input: String representing the filepath to the raw policy document (.txt).
    output: Object/Dictionary mapping string section numbers to their verbatim extracted text content.
    error_handling: Refuses to proceed and throws an exact error if the file cannot be found or if numbered sections cannot be successfully identified.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with explicit clause references, strictly preserving all multi-condition obligations.
    input: Object/Dictionary mapping section numbers to verbatim text content.
    output: String representing the final structured summary.
    error_handling: If a clause cannot be concisely summarized without meaning loss or softening obligations, it injects the verbatim quote directly into the output rather than guessing.

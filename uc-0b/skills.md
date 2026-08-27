skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents into structured, numbered sections and clauses.
    input: A string representing the file path of the policy text document.
    output: A dictionary/object mapping section numbers and clause numbers to their exact text contents.
    error_handling: If the file path is invalid, inaccessible, or the file is empty, raises a FileNotFoundError or ValueError.

  - name: summarize_policy
    description: Takes structured policy sections and generates a compressed, obligation-preserving summary referencing each clause.
    input: A dictionary/object containing structured policy clauses.
    output: A string containing the formatted summary with all clauses accounted for and binding verbs preserved.
    error_handling: If any mandatory clauses are missing from the input, or if a clause cannot be safely summarized without loss of meaning, the skill fails or quotes the clause verbatim with a warning flag.

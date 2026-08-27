# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and return its numbered sections in a structured form.
    input: A file path to a policy text document.
    output: A list of sections keyed by clause number.
    error_handling: If the file is missing or unreadable, raise a clear error.

  - name: summarize_policy
    description: Turn the structured policy clauses into a compliant summary that preserves the required clauses and conditions.
    input: A policy file path and output file path.
    output: A written summary file containing the required clause-preserving content.
    error_handling: If a clause cannot be summarized without loss, preserve it verbatim.

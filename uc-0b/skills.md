skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns numbered clauses grouped by section heading.
    input: Path to a .txt policy document.
    output: A structured list of section headings and numbered clauses with their full text.
    error_handling: Raise a clear error if the file cannot be read or no numbered clauses are found.

  - name: summarize_policy
    description: Produces a clause-preserving summary with clause references and verbatim fallback for risky clauses.
    input: Structured policy sections and clauses.
    output: Summary text with one line per clause plus section headers.
    error_handling: If a clause cannot be compressed safely, emit the clause as VERBATIM instead of paraphrasing.

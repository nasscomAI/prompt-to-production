skills:
  - name: retrieve_policy
    description: Loads the HR leave policy text file and returns it as structured numbered sections for downstream summarization.
    input: A .txt file path containing the source policy document.
    output: A structured representation of numbered clauses and their text content.
    error_handling: If the file cannot be read or no numbered clauses are found, return a clear error and do not fabricate sections.

  - name: summarize_policy
    description: Summarizes structured policy clauses into a compliant summary while preserving obligations, conditions, and clause references.
    input: Structured numbered policy sections.
    output: A text summary with clause references and clause-preserving statements.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and mark it for review instead of guessing.
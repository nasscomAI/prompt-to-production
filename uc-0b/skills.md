skills:
  - name: retrieve_policy
    description: Load a policy text file and structure it into numbered clauses and sections.
    input: A file path to a plain-text policy document.
    output: A list of clauses with clause numbers, headings, and full text.
    error_handling: If the file cannot be parsed, return a clear error and do not proceed to summarization.

  - name: summarize_policy
    description: Summarize the structured policy clauses while preserving meaning and clause references.
    input: Structured policy clauses from retrieve_policy.
    output: A multi-line summary string containing every numbered clause, especially the clause inventory entries, and any verbatim flags.
    error_handling: If any clause cannot be safely paraphrased, include it verbatim with a [FLAG] marker.

# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads the supplied policy text file and returns its contents as
      structured numbered policy clauses without changing the source text.
    input: >
      File path to a plain-text policy document.
    output: >
      Structured collection of policy clauses containing clause number,
      section, and original clause text.
    error_handling: >
      If the file does not exist, cannot be read, or contains no numbered
      policy clauses, return an explicit error and do not generate a summary.

  - name: summarize_policy
    description: >
      Produces a concise policy summary while preserving every numbered
      clause, obligation, condition, threshold, deadline, exception,
      approval requirement, and prohibition from the source.
    input: >
      Structured policy clauses returned by retrieve_policy.
    output: >
      Plain-text policy summary with clause references and all source
      requirements preserved.
    error_handling: >
      If the input is missing, incomplete, ambiguous, or cannot be summarized
      without meaning loss, flag the affected clause or refuse to guess.
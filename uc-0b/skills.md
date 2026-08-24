# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads the supplied HR policy text file and returns its numbered policy
      sections in a structured representation.
    input: >
      A path to a plain-text policy document.
    output: >
      A structured collection of numbered clauses containing each clause
      reference and its source text.
    error_handling: >
      If the file does not exist, cannot be read, or contains no numbered
      clauses, report an explicit error and stop rather than guessing.

  - name: summarize_policy
    description: >
      Produces a source-grounded summary of the required HR policy clauses
      while preserving every obligation and condition.
    input: >
      Structured numbered policy clauses from retrieve_policy.
    output: >
      A text summary containing all ten required clause references and their
      complete policy requirements.
    error_handling: >
      If any required clause is missing or its conditions cannot be preserved
      safely, fail explicitly instead of producing an incomplete summary.

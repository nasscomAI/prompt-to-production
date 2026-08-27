skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: File path to the policy text document.
    output: Structured representation of numbered sections and their text.
    error_handling: Return a structured error if the file is missing or cannot be parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured numbered sections from the retrieve_policy skill.
    output: A precise text summary explicitly referencing original clause numbers and preserving all conditions.
    error_handling: Quote the clause verbatim and flag it if the clause cannot be summarised without meaning loss or if conditions are ambiguous.

skills:
  - name: retrieve_policy
    description: Loads a text-based policy file and parses it into a structured format indexed by numbered sections and clauses.
    input: Path to a .txt policy file.
    output: A structured object where keys are clause numbers and values are the corresponding text.
    error_handling: Raises an error if the file is missing or if the numbering format is unrecognizable.

  - name: summarize_policy
    description: Generates a compliant summary of the structured policy sections while ensuring all obligations and conditions are retained.
    input: Structured policy content (dictionary of clauses).
    output: A summarized text document with explicit clause references and preserved conditions.
    error_handling: If a clause is missing from the summary, it must be re-added before final output.

skills:
  - name: retrieve_policy
    description: Load the HR policy document and extract structured numbered clauses.
    input: Path to a .txt policy document.
    output: Dictionary or list of numbered policy clauses.
    error_handling: If the file cannot be read or parsed, return an error and stop execution.

  - name: summarize_policy
    description: Generate a clause-preserving summary referencing each clause number.
    input: Structured policy clauses.
    output: Text summary referencing each clause number and preserving obligations.
    error_handling: If summarization would drop conditions or meaning, output the clause verbatim and label it VERBATIM.
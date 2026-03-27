skills:
  - name: retrieve_policy
    description: Loads the HR policy text file and extracts numbered policy clauses.
    input: Path to a .txt policy document containing numbered sections.
    output: Structured list or dictionary containing clause numbers and their text.
    error_handling: If the file cannot be read or has missing clauses, return an error message and stop processing.

  - name: summarize_policy
    description: Produces a compliant summary of the policy while preserving clause meaning and obligations.
    input: Structured clauses extracted from the policy document.
    output: Text summary referencing each clause and preserving all conditions.
    error_handling: If a clause cannot be summarized without losing meaning, return the original clause text and flag it.
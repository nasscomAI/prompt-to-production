skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses numbered clauses into structured sections.
    input: File path to a .txt policy document.
    output: Ordered list of section records with clause_number and clause_text.
    error_handling: Raises a clear file/parse error when the source file is missing or no numbered clauses are found.

  - name: summarize_policy
    description: Generates a clause-preserving summary from parsed policy sections.
    input: Ordered clause records from retrieve_policy.
    output: Summary text with one line per clause and section citations.
    error_handling: Falls back to verbatim quoting with [FLAG: VERBATIM] when safe paraphrase is not possible.

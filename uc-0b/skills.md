skills:
  - name: retrieve_policy
    description: Loads a policy text file and extracts numbered clauses.
    input: Path to a .txt policy document.
    output: List of structured clauses with clause number and text.
    error_handling: If the file cannot be read, return an empty clause list.

  - name: summarize_policy
    description: Produces a clause-preserving summary of the policy document.
    input: Structured clauses extracted from the policy.
    output: Summary text containing all clauses with preserved conditions.
    error_handling: If a clause cannot be summarized safely, output the clause verbatim and mark it for review.
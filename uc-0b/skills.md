skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts numbered clauses in source order.
    input: Path to a .txt policy document supplied through --input.
    output: A list of structured records with clause number and clause text.
    error_handling: Raises a clear error if the file has no numbered clauses or cannot be read.

  - name: summarize_policy
    description: Produces a compliant clause-preserving summary with clause references.
    input: Structured numbered sections returned by retrieve_policy.
    output: A plain-text summary that includes every clause number and preserves obligations, approvals, deadlines, forfeiture rules, and mandatory requirements.
    error_handling: Quotes clauses verbatim and flags them when summarization may lose meaning; rejects duplicate or malformed clause records and prohibited scope-bleed phrases.

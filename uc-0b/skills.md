# skills.md - UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts structured numbered clauses.
    input: Path to a UTF-8 text policy file.
    output: A list of dictionaries, each with clause and text fields.
    error_handling: If the file cannot be read, the caller receives the file error; unnumbered text is ignored unless it belongs to the current numbered clause.

  - name: summarize_policy
    description: Produces a clause-preserving summary with explicit references to every numbered policy clause.
    input: A list of structured clauses from retrieve_policy.
    output: A text summary where each numbered clause has one meaning-preserving summary line.
    error_handling: Unknown clauses are quoted verbatim and marked NEEDS_REVIEW; missing required clauses are listed as NEEDS_REVIEW instead of being guessed.

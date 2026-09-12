skills:
  - name: retrieve_policy
    description: Loads a UTF-8 plain-text policy and returns its numbered clauses as structured records.
    input: A filesystem path to a .txt policy document.
    output: A list of records containing clause number and normalized source text, in source order.
    error_handling: Rejects missing, unreadable, empty, or clause-free files with a clear error; preserves the source text instead of guessing when parsing is ambiguous.
  - name: summarize_policy
    description: Produces a clause-referenced policy summary without dropping obligations or conditions.
    input: A list of structured policy clause records from retrieve_policy.
    output: UTF-8 plain text containing every clause reference and its source-derived obligation.
    error_handling: Rejects empty or malformed clause records; quotes the source clause and marks it for review when meaning cannot be safely compressed.

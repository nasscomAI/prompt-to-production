skills:
  - name: retrieve_policy
    description: Load a .txt policy file and parse it into structured numbered clauses.
    input: File path string pointing to a UTF-8 text policy document.
    output: Ordered list of objects with clause_number, section_title, and clause_text.
    error_handling: Raise a clear error when file is missing, unreadable, or contains no numbered clauses.

  - name: summarize_policy
    description: Generate a clause-referenced summary that preserves obligations and conditions.
    input: Ordered structured clauses from retrieve_policy.
    output: Plain-text summary grouped by section with clause numbers and faithful wording.
    error_handling: If a clause cannot be summarized without meaning loss, include an exact-text line tagged as verbatim.

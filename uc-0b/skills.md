# skills.md — UC-0B Skills

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses it into a document header plus structured sections, each with its numbered clauses and full clause text.
    input: File path (string) to the .txt policy document.
    output: A dictionary with raw_text, header (title/document reference/version lines), sections (list of {title, clauses:[{num, text}]}), and clause_count.
    error_handling: Raises FileNotFoundError with a clear message if the file is missing; reads UTF-8 safely; skips separator/blank lines so only real content is captured.

  - name: summarize_policy
    description: Renders a lossless, clause-by-clause policy summary that preserves every numbered clause and every multi-condition obligation (e.g. dual approvers) verbatim.
    input: Structured policy data (dict) produced by retrieve_policy.
    output: A structured text summary listing every section and every clause with its number and exact text, so no clause is omitted, no condition is dropped, and no binding verb is softened.
    error_handling: Never adds information not in the source document; keeps the source text verbatim when a clause cannot be safely reworded.

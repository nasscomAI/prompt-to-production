skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its full content as a string.
    input: file_path (str) — path to the .txt policy document.
    output: str — full text content of the policy file.
    error_handling: Raises FileNotFoundError with the path if the file cannot be opened. Never silently returns an empty string.

  - name: summarize_policy
    description: Takes policy text and produces a structured clause-by-clause summary, preserving all numbered clauses and their exact obligations.
    input: policy_text (str) — full text of the policy document.
    output: str — formatted summary with every numbered clause present; obligations are extracted verbatim so no binding verb or condition can be softened.
    error_handling: If a clause section is missing from the input, writes "[CLAUSE X.X NOT FOUND — REVIEW REQUIRED]" in its place rather than silently omitting it.

# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and extract numbered clauses into structured sections.
    input: A file path to a `.txt` policy document.
    output: A dictionary mapping clause numbers to clause text.
    error_handling: If the file is missing or unreadable, raise a clear error. If clause text cannot be parsed, capture the raw text and include a warning.

  - name: summarize_policy
    description: Produce a compliant summary from structured clause sections that retains all required clause meanings.
    input: A dictionary of numbered sections extracted from the policy file.
    output: A text summary with each required clause referenced explicitly.
    error_handling: If a required clause is missing or ambiguous, note the gap in the summary and preserve the original clause text verbatim rather than inventing a replacement.

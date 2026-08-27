skills:
  - name: retrieve_policy
    description: Loads the input plain text policy document and parses it into structured sections and numbered clauses.
    input: input_path (str) to the source text policy file.
    output: dict mapping clause numbers (e.g., "2.3") to their verbatim text content.
    error_handling: Raises FileNotFoundError if the file path is incorrect, or returns an empty dictionary if the file is blank.

  - name: summarize_policy
    description: Processes parsed clauses and drafts a concise summary verifying completeness and condition retention.
    input: clauses (dict) containing clause numbers and raw text.
    output: str representing the formatted text summary of all required clauses.
    error_handling: If any required clause (from the ground-truth list) is missing, it falls back to quoting the clause verbatim or raises a validation error.

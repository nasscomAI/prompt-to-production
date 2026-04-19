skills:
  - name: retrieve_policy
    description: Loads HR policy text file and returns raw content as string.
    input: Dictionary with 'input_path' (str): absolute path to .txt policy file.
    output: String containing full raw policy text.
    error_handling: Raise FileNotFoundError if path invalid; return empty string if read fails.

  - name: summarize_policy
    description: Parses raw policy text into structured Markdown summary preserving all clauses exactly.
    input: String: raw policy text.
    output: Markdown string with title, effective date, sectioned clauses.
    error_handling: If 0 clauses or <20 detected, raise ValueError "Insufficient clauses or parsing failed".

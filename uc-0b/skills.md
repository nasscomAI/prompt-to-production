skills:
  - name: retrieve_policy
    description: Reads the input HR policy text file.
    input: File path string
    output: Raw text string
    error_handling: Raise FileNotFoundError if file is missing.
  - name: summarize_policy
    description: Summarizes obligations preserving all rules.
    input: Raw text string
    output: Summary string
    error_handling: Refuse to summarize if content is ambiguous.

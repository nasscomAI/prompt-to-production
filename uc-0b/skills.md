skills:
  - name: retrieve_policy
    description: Reads and parses the input HR policy text document.
    input:
      input_path: string
    output:
      content: string
    error_handling: Raise an error if the input file path is missing or unreadable.

  - name: summarize_policy
    description: Summarizes policy content while preserving all binding obligations and conditions.
    input:
      content: string
    output:
      summary: string
    error_handling: Return refusal notice if text is corrupt or non-policy format.
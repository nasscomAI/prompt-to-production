skills:
  - name: retrieve_policy
    description: Reads and returns the full text content of the HR leave policy file from the specified file path.
    input:
      type: string
      format: Absolute or relative file path pointing to a .txt policy document
    output:
      type: string
      format: Full raw text content of the policy document
    error_handling: >
      If the file path does not exist, is not readable, or the file is empty,
      the skill must raise an error with the message "Policy file not found or
      unreadable: [path]" and halt execution. It must not return partial
      content or an empty string silently.

  - name: summarize_policy
    description: Produces a structured summary of the HR leave policy text preserving all binding obligations, conditions, and numerical values.
    input:
      type: string
      format: Full text of the HR leave policy as returned by retrieve_policy
    output:
      type: string
      format: Structured plain-text summary organised by leave type, with each binding rule, eligibility condition, and numerical value listed explicitly
    error_handling: >
      If the input text is empty or shorter than 50 characters, the skill must
      refuse to summarise and return the message "Input policy text is
      insufficient for summarisation." If a clause contains multiple conditions,
      all conditions must be included; if any condition cannot be parsed, the
      original clause must be quoted verbatim rather than omitted. The skill
      must not add information absent from the input text.

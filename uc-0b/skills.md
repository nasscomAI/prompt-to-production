skills:
  - name: retrieve_policy
    description: >
      Loads the HR policy text file and organizes it into structured,
      numbered policy sections for processing.
    input: >
      Path to a plain text (.txt) HR policy document.
    output: >
      Structured policy sections with clause numbers and corresponding text.
    error_handling: >
      If the file cannot be read or is invalid, return an error message.
      If clause numbering is missing, preserve the available text and
      indicate the missing structure.

  - name: summarize_policy
    description: >
      Generates a compliant summary of the policy while preserving every
      clause, obligation, approval requirement, and restriction.
    input: >
      Structured policy sections produced by retrieve_policy.
    output: >
      A policy summary with clause references that preserves all mandatory
      conditions and obligations.
    error_handling: >
      If a clause cannot be summarized without changing its meaning,
      quote the original clause verbatim and flag it instead of
      modifying or omitting it.
# skills.md — UC-0B HR Policy Summarizer

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path string to the .txt policy document.
    output: A list or dictionary of structured numbered sections of the policy.
    error_handling: Raises an exception if the file cannot be found or read.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured sections from retrieve_policy.
    output: A summary string with exact clause references and all conditions preserved.
    error_handling: If a clause cannot be summarised without meaning loss, it quotes it verbatim and flags it.

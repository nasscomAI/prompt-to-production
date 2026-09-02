# skills.md — UC-0B Policy Summarizer Skills

skills:
  - name: retrieve_policy
    description: Loads an input .txt policy file and returns the content broken into structured numbered sections.
    input: File path string pointing to the policy text document.
    output: String or dictionary containing structured numbered sections.
    error_handling: Raises FileNotFoundError with a clear message if the file is missing or unreadable.

  - name: summarize_policy
    description: Processes structured policy sections to generate a summary preserving all binding verbs, numeric conditions, and multi-condition rules.
    input: Raw policy text or structured sections string.
    output: Compliant text summary containing clause-by-clause details and verification flags.
    error_handling: Appends a flag and quotes complex clauses verbatim if rule extraction introduces ambiguity.
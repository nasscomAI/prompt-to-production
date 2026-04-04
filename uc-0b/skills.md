# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents into structured numbered clauses and sections.
    input: Filepath to the policy text document.
    output: A structured dictionary mapping section headers to their respective numbered clauses.
    error_handling: Return an I/O error or empty structure if the file is missing or unreadable, safely halting the pipeline.

  - name: summarize_policy
    description: Takes structured clauses and returns a legally-compliant summary maintaining all strict conditions and obligations.
    input: Structured document dictionary from retrieve_policy.
    output: A formatted plain-text summary preserving all numbered clauses and their multi-condition requirements.
    error_handling: If a clause's complexity risks dropping conditions during condensation, the skill must return the verbatim clause flagged with [VERBATIM].

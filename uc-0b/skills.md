skills:
  - name: retrieve_policy
    description: Loads the HR leave policy from a text file and returns it as structured numbered sections.
    input: A .txt policy file containing numbered HR leave policy sections.
    output: Structured policy sections with clause numbers and original content.
    error_handling: If the file is missing, unreadable, or incomplete, report the error and do not guess or create missing information.

  - name: summarize_policy
    description: Summarizes every numbered HR leave policy clause while preserving all conditions, requirements, dates, limits, approvals, exceptions, and restrictions.
    input: Structured numbered HR leave policy sections from retrieve_policy.
    output: A concise summary containing every clause reference and all important conditions.
    error_handling: If a clause cannot be safely summarized without changing its meaning, quote the clause verbatim and mark it [VERBATIM].
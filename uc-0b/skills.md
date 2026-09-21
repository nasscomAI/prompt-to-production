skills:
  - name: retrieve_policy
    description: Loads the HR policy text and returns its numbered clauses as structured sections.
    input: "UTF-8 policy text file path."
    output: "Ordered list of clause records containing section number and source text."
    error_handling: "Rejects missing or unreadable files and reports required clauses that cannot be found instead of silently omitting them."

  - name: summarize_policy
    description: Produces a clause-referenced summary that preserves all required obligations and conditions.
    input: "Structured policy clause records containing section numbers and source text."
    output: "UTF-8 text summary containing every required clause reference and its faithful obligation."
    error_handling: "Quotes and marks a clause verbatim when summarizing could lose meaning; never invents or softens an obligation."

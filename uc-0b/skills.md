skills:
  - name: retrieve_policy
    description: Loads a plain text policy document (.txt) and parses it into structured numbered sections and clauses.
    input: File path to the policy text document (e.g., policy_hr_leave.txt).
    output: Structured dictionary/object mapping section numbers and titles to individual clause texts.
    error_handling: Raises FileNotFoundError if file is missing, or ValueError if document structure is corrupted or unreadable.

  - name: summarize_policy
    description: Takes structured section data and produces a compliant, clause-by-clause summary preserving all binding obligations and condition dependencies.
    input: Structured policy section object from retrieve_policy.
    output: Formatted string text summary with clause citations, preserving all dual-approval and numerical constraints.
    error_handling: If a clause contains ambiguous or complex multi-part conditions that cannot be compressed safely, quotes the clause verbatim and appends a [VERBATIM_PRESERVED] flag.

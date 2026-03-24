skills:
  - name: retrieve_policy
    description: Loads the policy text file and parses it into ordered numbered clauses.
    input: Input file path to a UTF-8 .txt policy document.
    output: Ordered list of clause objects with clause_id and clause_text.
    error_handling: Raises clear error if file is missing or no numbered clauses are found.

  - name: summarize_policy
    description: Produces a faithful clause-by-clause summary preserving obligations and conditions.
    input: Ordered list of clause objects from retrieve_policy.
    output: Multi-line summary text where each line begins with clause number and concise faithful summary.
    error_handling: Falls back to near-verbatim clause text with [STRICT_WORDING_RETAINED] when safe compression is uncertain.

skills:
  - name: retrieve_policy
    description: Loads a raw text policy document (.txt) and parses it into structured numbered sections and clauses.
    input: input_path (str) - path to text policy file
    output: dict or list of structured sections containing section titles and individual numbered clause strings
    error_handling: Raises FileNotFoundError if file missing, or ValueError if text format is empty.

  - name: summarize_policy
    description: Generates a clause-by-clause compliant executive summary that preserves all mandatory binding obligations, dual-approval requirements, and forfeiture constraints without scope bleed.
    input: structured_policy (dict or list) - parsed sections and clauses from retrieve_policy
    output: formatted text summary string with clause citations for each obligation
    error_handling: Flags missing or unparseable clauses explicitly in the summary.


skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured section headers, numbered clauses, and binding verbs.
    input: File path string to the policy text document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: List of structured section objects, each containing section title, list of clauses with clause number, exact text, extracted binding verbs, and condition flags.
    error_handling: Validates file existence and readability; raises FileNotFoundError if missing, or returns fallback unparsed structure with warning flag if text formatting is non-standard.

  - name: summarize_policy
    description: Processes structured policy sections and generates a comprehensive, clause-faithful summary adhering strictly to all zero-loss enforcement rules.
    input: Structured section objects returned by retrieve_policy.
    output: Formatted text string representing the complete policy summary with section headers, clause numbers, preserved binding verbs, multi-condition criteria, and verbatim quotes for complex clauses.
    error_handling: Checks every output clause against source ground-truth clauses; if any condition is missing or binding verb is weakened, quotes the clause verbatim and appends warning flag '[VERBATIM QUOTE - AMBIGUITY PREVENTED]'.

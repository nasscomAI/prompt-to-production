skills:
  - name: retrieve_policy
    description: Loads the policy document and returns its contents structured as numbered sections.
    input: File path string pointing to the policy document (e.g. policy_hr_leave.txt).
    output: A string containing the raw text of the structured numbered sections.
    error_handling: Raise a FileNotFoundError if the policy document cannot be found or read.

  - name: summarize_policy
    description: Generates a highly accurate summary strictly adhering to the 10 target clauses, quoting them accurately without dropping conditions.
    input: A string of the structured policy content retrieved by retrieve_policy.
    output: A compliant summary string highlighting the specifically requested obligations.
    error_handling: If extraction fails or a clause is missing, loudly fail rather than hallucinating text.

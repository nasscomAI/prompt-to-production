skills:
  - name: retrieve_policy
    description: Loads the plaintext policy file and returns the content grouped into structured, numbered sections.
    input: File path to the plaintext policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured text or dictionary mapping section numbers to their text.
    error_handling: Raises an error if the file is not found or fails to map the expected numbered clauses.

  - name: summarize_policy
    description: Takes the structured sections from the policy and produces a compliant summary that perfectly preserves all obligations and constraints.
    input: Structured sections or text output from retrieve_policy.
    output: A newly generated compliant summary containing all mapped clauses.
    error_handling: If a clause formulation is too complex to summarize without risk of meaning loss, it quotes the clause verbatim and appends a flag to it.

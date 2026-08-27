# skills.md

skills:
  - name: retrieve_policy
    description: Opens and reads the policy document, parsing it into structured sections indexed by clause number.
    input: File path to the HR policy text file (e.g., `data/policy-documents/policy_hr_leave.txt`).
    output: A dictionary mapping clause numbers (e.g., "5.2") to their full text.
    error_handling: Return a clear error if the file is missing or formatted in a way that prevents clause identification.

  - name: summarize_policy
    description: Generates a condition-preserving summary based on the agent's enforcement rules and specific clauses retrieved.
    input: Dictionary of clauses and their text.
    output: A structured summary string with specific references to clause numbers and and preserved conditions.
    error_handling: If a clause contains ambiguous logic, quote it verbatim and flag it for manual review.

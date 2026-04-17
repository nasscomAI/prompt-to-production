# skills.md

skills:
  - name: retrieve_policy
    description: Loads the raw .txt policy file and parses its contents into structured, numbered sections.
    input: Filepath to the raw policy text document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured text or JSON representation of the policy content, strictly broken down by original numbered clauses.
    error_handling: If the file is missing, unreadable, or empty, throw an error and refuse to proceed rather than guessing.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary that preserves exact clause references, binding verbs, and all conditions.
    input: Structured policy content broken down by numbered clauses (produced by retrieve_policy).
    output: A complete, compliant summary text document where every summary point explicitly refers to its clause number.
    error_handling: If any clause cannot be condensed without softening obligations or dropping conditions, quote the specific clause verbatim and explicitly flag it in the output.
    prompt =f"Please summarize the following policy document according to your strict enforcement rules:\n\n{text}"

skills:
  - name: retrieve_policy
    description: Opens and reads the raw policy text file parsing it into a structured format containing numbered sections.
    input: Filepath to the policy text document (e.g. `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured object containing the safely loaded, numbered sections.
    error_handling: If the file is missing or unreadable, halt execution and raise a FileNotFoundError to prevent processing empty strings.

  - name: summarize_policy
    description: Receives structured policy sections and produces a compliant summary preserving all binding clauses and conditions.
    input: The structured, numbered sections outputted by retrieve_policy.
    output: A final formatted string containing the compliant HR policy summary incorporating clause references.
    error_handling: If any clause is completely unsummarizable without losing meaning, quote the clause verbatim in the output and append a [VERBATIM] flag.

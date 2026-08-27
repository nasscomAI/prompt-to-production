skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: A string file path to the .txt policy file (e.g., policy_hr_leave.txt).
    output: A formatted string or object containing the content structured as numbered sections.
    error_handling: Return an error message indicating the failure to load the policy if the file is missing or unreadable.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with correct clause references and maintaining all condition requirements.
    input: Structured numbered policy sections.
    output: A summary string containing precise clause references without any meaning loss, obligation softening, or omitted conditions.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it.

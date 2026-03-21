skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into structured numbered sections.
    input: File path to the .txt policy document (e.g., policy_hr_leave.txt).
    output: Ordered list of numbered sections, each containing the section number and its full text content.
    error_handling: If the file is not found or cannot be parsed, return an error message with the file path and stop processing.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary with clause references, preserving all obligations and binding verbs.
    input: Ordered list of numbered sections returned by retrieve_policy.
    output: Plain text summary written to the output file (e.g., summary_hr_leave.txt), where every clause is referenced by number and no conditions are dropped.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and append flag VERBATIM_REQUIRED at the end of that clause entry.

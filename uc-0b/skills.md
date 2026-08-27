skills:
  - name: retrieve_policy
    description: Parses the raw .txt policy document into structured and numbered sections.
    input: Filepath to the raw policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured dictionary mapping clause numbers to their exact textual content.
    error_handling: Notifies the user if the document is completely unformatted and lacks numbered clauses to extract.

  - name: summarize_policy
    description: Converts structured policy clauses into a compliant summary, rigorously preserving dual-conditions and verb bindings. 
    input: The structured clauses obtained from retrieve_policy.
    output: A text file representing the accurate summary of the policy, mapped directly to original clause numbers.
    error_handling: Reverts to quoting the exact text verbatim and appending a [NEEDS_REVIEW] flag if attempting to summarize the text risks omitting conditions.

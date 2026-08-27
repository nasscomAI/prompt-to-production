skills:
  - name: retrieve_policy
    description: "loads .txt policy file, returns content as structured numbered sections"
    input: "String file path to the policy document (e.g., '../data/policy-documents/policy_hr_leave.txt')."
    output: "A dictionary mapping clause numbers (e.g., '2.3') to their corresponding text content."
    error_handling: "If the file is missing or unreadable, return a clear error stating the file could not be accessed."

  - name: summarize_policy
    description: "takes structured sections, produces compliant summary with clause references"
    input: "Dictionary of numbered clauses."
    output: "A string containing the final compliant summary formatted as a textual document."
    error_handling: "If any clause is ambiguous or cannot be summarized without loss of meaning, quote it verbatim and add a [FLAGGED FOR REVIEW] tag."

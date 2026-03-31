skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from the provided file path and returns its content as structured, numbered sections.
    input: String representing the file path of the policy document (e.g., '../data/policy-documents/policy_hr_leave.txt').
    output: A list or structured string containing all policy clauses completely intact, organized by their numbering.
    error_handling: Return an error if the file is not found at the specified path, or if the file cannot be read correctly.

  - name: summarize_policy
    description: Takes structured sections of the extracted policy text and produces a lossless, compliant summary with explicit clause references, maintaining all multi-condition obligations without softening them.
    input: Organized text or sections returned by the `retrieve_policy` skill.
    output: String representing the final, precise policy summary containing every numbered clause from the original document and strictly omitting external or standard-practice information.
    error_handling: Raise an error if the summary drops any numbered clause, misses any multi-condition rule (e.g., dropping a needed second approver), or if scope bleed is detected (injecting outside knowledge).

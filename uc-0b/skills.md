skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: File path string to the policy document (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: A structured list of objects or text blocks, each representing a discrete, numbered clause from the document.
    error_handling: Raises an error if the file is missing or unreadable. If the document lacks numbered clauses, refuse to process and return an error rather than inventing sections.

  - name: summarize_policy
    description: Takes structured document sections and produces a compliant summary with exact clause references.
    input: A structured list of numbered clauses (the output from retrieve_policy).
    output: A concise text summary that references each clause and explicitly maps all core obligations and multi-condition rules.
    error_handling: If a clause contains ambiguous multi-conditions or cannot be distilled safely, return the exact verbatim quote with a warning flag instead of guessing the intent.

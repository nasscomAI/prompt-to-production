# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: File path (string).
    output: List of structured objects/sections (JSON/Dict).
    error_handling: Return an error if the file path is invalid or the document is not a policy file.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: List of structured sections (JSON/Dict).
    output: Formatted summary text (markdown).
    error_handling: Refuse to summarize if clause numbers are missing or core obligations are dropped.
    clause_inventory:
      hr_leave: [2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2]
      it_use: [3.5, 4.4, 5.1, 5.2, 7.3]
      finance_reimbursement: [1.3, 2.1, 3.2, 5.2, 6.4]


# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: summarize_policy
    description: Summarizes the HR leave policy, preserving all obligations and scope.
    input: The full text of policy_hr_leave.txt.
    output: A summary text containing all 10 clauses, each with its core obligation and binding verb.
    error_handling: If any clause is missing or ambiguous, output NEEDS_REVIEW and specify which clause failed.

  - name: clause_inventory_check
    description: Checks the summary for presence and accuracy of all 10 clauses and binding verbs.
    input: The summary text and the clause inventory from the README.
    output: A report listing any missing, merged, or softened clauses, and any changes to binding verbs.
    error_handling: If summary fails inventory check, output NEEDS_REVIEW and list discrepancies.

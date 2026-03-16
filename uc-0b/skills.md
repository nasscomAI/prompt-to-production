skills:
  - name: retrieve_policy
    description: Retrieves the policy document based on the policy name.
    input: .txt policy file
    output: content as structured numbered sections
    error_handling: If policy not found, return "Policy not found"

  - name: summarize_policy
    description: Summarizes the policy document into easily readable format: ex: "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1" to be summarized to "14-day advance notice required"
    input: .txt policy file
    output: summary of the policy document
    error_handling: If policy not found, return "Policy not found"

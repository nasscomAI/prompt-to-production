skills:
  - name: extract_leave_policy
    description: Extract relevant leave policy information from the HR policy text file.
    input: policy_hr_leave.txt containing HR leave policy text.
    output: Structured information about leave types, eligibility rules, and limits.
    error_handling: If required information cannot be found in the document, return "NOT_FOUND" and flag the query for review.

  - name: answer_leave_query
    description: Answer an employee question about leave policy using the extracted HR policy rules.
    input: Employee question (string) and policy text from policy_hr_leave.txt.
    output: A concise answer explaining the applicable leave rule and referencing the policy text.
    error_handling: If the question cannot be answered using the policy document, return "INSUFFICIENT_POLICY_INFORMATION".
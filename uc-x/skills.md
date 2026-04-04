skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt
    output: Indexed documents mapped by document name and section number
    error_handling: Return an error if any file fails to load or if section numbering is missing

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: User's question and the indexed policy documents
    output: Single-source answer with citation (document name + section number) OR the refusal template
    error_handling: |
      If the question is not covered or requires blending multiple documents, return the exact refusal template:
      This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance.

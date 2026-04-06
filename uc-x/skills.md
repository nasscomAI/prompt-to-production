skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input:
      type: list
      format:
        - "../data/policy-documents/policy_hr_leave.txt"
        - "../data/policy-documents/policy_it_acceptable_use.txt"
        - "../data/policy-documents/policy_finance_reimbursement.txt"
    output:
      type: dictionary
    error_handling: |
      If any document is missing, raise a File Not Found error.

  - name: answer_question
    description: Searches indexed documents for an answer and returns citation or refusal.
    input:
      type: string
    output:
      type: string
    error_handling: |
      If not found, return the exact refusal template from agents.md.
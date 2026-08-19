skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number.
    input:
      documents:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
    output:
      index:
        key_fields:
          - document_name
          - section_number
        value_fields:
          - section_text
    error_handling:
      - If any required document is missing or unreadable, return an error identifying the missing file(s) and stop.
      - If section parsing fails, return an error with the affected document name and stop.

  - name: answer_question
    description: Answers a policy question from a single document only with citation, or returns the refusal template.
    input:
      question: string
      index:
        key_fields:
          - document_name
          - section_number
        value_fields:
          - section_text
    output:
      answer: string
      citation:
        document_name: string
        section_number: string
      source_scope: single_document_only
    error_handling:
      - If answer not found, return exactly: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
      - If multiple documents match, do not merge; choose one document or return exactly: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
      - If only partial information is available, do not guess; return exactly: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.

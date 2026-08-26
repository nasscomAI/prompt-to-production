skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy documents by document name and section number.
    input: File paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Searchable index mapping keywords to source text with document and section metadata.
    error_handling: Raises clear error if any file is missing or section parsing fails.

  - name: answer_question
    description: Returns a single-source policy answer with citation or exact refusal template.
    input: User question string and indexed policy data.
    output: One answer string containing either policy claim with citation or refusal template.
    error_handling: Refuses when not covered or when answer would require cross-document blending.

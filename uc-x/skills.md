skills:
  - name: retrieve_documents
    description: "Loads all 3 policy files and indexes them by document name and section number."
    input: "Policy documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output: "Indexed collection of document content mapped to document names and section numbers."
    error_handling: "If any policy file is missing or unreadable, stop execution. If indexing fails, report source error."

  - name: answer_question
    description: "Searches indexed documents to return a single-source answer with citation or the refusal template."
    input: "User query (string) and the indexed document repository."
    output: "A single-source answer string with citation (Document Name + Section #) or the exact refusal template."
    error_handling:
      - "If multiple documents match: Do not combine; return refusal."
      - "If no answer found: Return the refusal template."
      - "If ambiguous: Return the refusal template."
      - "Refusal Template: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'"

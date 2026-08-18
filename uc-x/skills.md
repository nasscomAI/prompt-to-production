# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Indexed text content structured by document and section.
    error_handling: Refuse to answer if source documents are missing or fail to load.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: User question string and indexed documents.
    output: String response containing factual answer + citations OR exact refusal template.
    error_handling: Return refusal template if answer is ambiguous or spread across multiple sources incorrectly.

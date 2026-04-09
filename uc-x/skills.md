skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of paths to policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Indexed documents mapped by document name and section numbers.
    error_handling: Throw an error if a policy document file is missing or corrupted.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR the exact refusal template.
    input: User question as string and indexed policy documents.
    output: A single-source answer string with document and section citation OR the exact refusal template string.
    error_handling: Output the exact refusal template if a multi-document blend is required or if the answer is not present.

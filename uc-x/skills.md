skills:
  - name: retrieve_documents
    description: Load all three policy files and build an index keyed by document name and section number.
    input: A request to load the policy corpus; the files are policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt under ../data/policy-documents/.
    output: An indexed collection containing each document name, section number, section text, and source path.
    error_handling: If a required file cannot be loaded or parsed into sections, report the specific file and stop; do not create a partial index or infer missing content.

  - name: answer_question
    description: Search the indexed policy documents and return a concise answer supported by one source document and a section citation, or the exact refusal template.
    input: A user's policy question as text and the indexed collection returned by retrieve_documents.
    output: A factual answer using only one policy document, followed by the source document name and section number; or exactly: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: If no single document directly covers the question, if the evidence is genuinely ambiguous across documents, or if the index is unavailable, return the exact refusal template. Never blend claims across documents, drop policy conditions, or fill gaps with general knowledge or hedging.

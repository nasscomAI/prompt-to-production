skills:
  - name: retrieve_documents
    description: Loads and indexes policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt by document name and section number.
    input: Path to policy-documents directory
    output: Dict of indexed document contents grouped by document name and section number.
    error_handling: Handles missing document files gracefully.

  - name: answer_question
    description: Evaluates a user prompt against indexed documents, enforcing single-source retrieval and exact refusal formatting.
    input: Question string
    output: Answer string with document name + section citation OR verbatim refusal template.
    error_handling: Refuses immediately if question requires blending multi-document claims or contains out-of-scope queries.

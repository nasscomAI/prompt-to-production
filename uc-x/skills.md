# skills.md
skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes text by document and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Searchable in-memory index of sections with document name, section id, and section text.
    error_handling: If any required document cannot be loaded or has no numbered sections, fail with a clear error before answering any question.

  - name: answer_question
    description: Returns a single-source cited answer from indexed policies or exact refusal template.
    input: User question string plus document index from retrieve_documents.
    output: Either Answer + Source citation (doc + section) from one document only, or the exact refusal template when unsupported/ambiguous.
    error_handling: On ambiguous matches across documents or insufficient evidence, refuse using the exact template and do not guess.

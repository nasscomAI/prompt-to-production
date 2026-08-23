skills:
  - name: retrieve_documents
    description: Load the three policy files and index their numbered sections without merging their contents.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Document-indexed sections keyed by source filename and section number.
    error_handling: Report a missing or unreadable document clearly and do not substitute another source.

  - name: answer_question
    description: Find a single-source answer with document and section citation or return the exact refusal template.
    input: Natural-language policy question and indexed documents.
    output: Clear answer with one source citation, or the required refusal text.
    error_handling: Refuse when no single source supports the answer or when answering would require blending documents.

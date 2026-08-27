skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes their sections and clauses by document name and section number.
    input: List of file paths or directory path containing policy documents.
    output: Dictionary mapping document names to structured lists of sections and clauses with section numbers, titles, and clause text.
    error_handling: Validates file existence and formatting; raises FileNotFoundError if files are missing, or handles unreadable files gracefully.

  - name: answer_question
    description: Queries indexed policy documents, matches intent to single-source sections, enforces cross-document non-blending guardrails, attaches document citations, or returns exact refusal template for out-of-scope questions.
    input: Question string and indexed documents structure returned by retrieve_documents.
    output: String response containing single-source policy answer with section citations OR exact refusal template.
    error_handling: Returns exact refusal template if question cannot be answered from policy documents or if multi-document blending would be required.

# skills.md - UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes content by document name and section number.
    input: Optional base directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A nested dictionary keyed by document name, then section number, with section text values.
    error_handling: Missing or unreadable policy files raise the underlying file error so the CLI fails visibly rather than answering from incomplete documents.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation or the exact refusal template.
    input: A user question string and the indexed documents from retrieve_documents.
    output: A text answer ending with source document and section number, or the exact refusal template.
    error_handling: Uncovered, ambiguous, or cross-document questions return the refusal template instead of a hedged or blended answer.

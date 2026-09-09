# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number for single-source lookups.
    input: list of paths — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: dict — mapping of document name to its sections keyed by section number, ready for lookups.
    error_handling: If any file is missing or unreadable, raises a clear error; sections that cannot be parsed are logged and reported instead of silently merged across documents.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source answer with citation, or the exact refusal template if the question is not covered.
    input: str — the user's question; dict — indexed documents from retrieve_documents.
    output: str — either an answer citing one document name and section number, or the exact refusal template verbatim.
    error_handling: If the question spans two documents or is ambiguous, returns the refusal template rather than blending; if no document matches, refuses cleanly with the template and never hedges or guesses.
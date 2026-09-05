# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: Paths to the three policy .txt files (policy_hr_leave, policy_it_acceptable_use, policy_finance_reimbursement).
    output: An index mapping each document name to its numbered sections and clause texts.
    error_handling: Raises an error if a file is missing, unreadable, or contains no numbered sections.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the refusal template.
    input: A question string plus the indexed documents from retrieve_documents.
    output: A single-source answer citing document name + section number, or the exact refusal template if not covered.
    error_handling: Refuses (never blends, never hedges) when the question requires combining documents or is not covered.
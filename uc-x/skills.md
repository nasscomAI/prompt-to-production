# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy text documents by section number.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Searchable index mapping filename and section number to section text.
    error_handling: If any required file is missing or unreadable, return a hard error and refuse to answer.

  - name: answer_question
    description: Returns a single-source cited answer or exact refusal template for policy questions.
    input: User question string and indexed policy documents.
    output: One answer text with either filename+section citation or exact refusal template.
    error_handling: If no reliable single-source match exists or match is cross-document ambiguous, return exact refusal template.

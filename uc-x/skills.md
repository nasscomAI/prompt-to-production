skills:
  - name: retrieve_documents
    description: Loads and indexes policy documents by document name and section number for retrieval.
    input: >
      File paths to policy documents:
      - policy_hr_leave.txt
      - policy_it_acceptable_use.txt
      - policy_finance_reimbursement.txt
    output: >
      Structured data containing:
      - document name
      - section number
      - section content
    error_handling: >
      If any document is missing or unreadable, return an error and stop execution.
      Do not proceed with partial data.

  - name: answer_question
    description: Answers a user question using a single policy document section or returns a refusal.
    input: >
      - User question (string)
      - Indexed policy documents (from retrieve_documents)
    output: >
      Either:
      1. A single-source answer with:
         - exact statement from document
         - document name
         - section number
      OR
      2. Refusal template (verbatim, no modification)
    error_handling: >
      - If multiple documents contain partial answers → REFUSE (do not combine)
      - If no exact match is found → REFUSE
      - If ambiguity exists → REFUSE
      - Never guess, infer, or generate blended responses
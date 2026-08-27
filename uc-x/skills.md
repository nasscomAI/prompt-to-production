# skills.md

skills:
  - name: retrieve_documents
    description: >
      Load all 3 policy .txt files and index them by document name and
      section number for efficient lookup.
    input: |
      List of 3 file paths: [policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt].
    output: |
      dict[str, str] — mapping from document name to full text content.
    error_handling: >
      If any file is missing or unreadable, raise FileNotFoundError with
      the missing file path.

  - name: answer_question
    description: >
      Search the indexed documents for an answer to the user's question.
      Return a single-source answer with source document name and section
      number, or the refusal template if no document covers the question.
    input: |
      question (str) — the user's natural language question.
      documents (dict[str, str]) — loaded document texts.
    output: |
      str — answer with citation (e.g., "policy_hr_leave.txt, Section 2.6:
      ...") or the refusal template.
    error_handling: >
      If the question matches content from multiple documents, return the
      most specific single-document answer. If genuinely ambiguous, use
      the refusal template. Never blend answers.

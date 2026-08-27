skills:
  - name: retrieve_documents
    description: >
      Loads and indexes the available policy documents by document name
      and section number for accurate retrieval.
    input: >
      Three policy text files:
      policy_hr_leave.txt,
      policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      Structured document index containing document name,
      section number, and section content.
    error_handling: >
      If a document is missing or cannot be read, report the filename
      and stop processing rather than using incomplete information.

  - name: answer_question
    description: >
      Searches the indexed policy documents and answers using a single
      source document only.
    input: >
      User question (string) and structured document index.
    output: >
      Answer with the supporting document name and section number,
      or the exact refusal template if the question is not covered.
    error_handling: >
      If multiple documents appear relevant or the answer cannot be
      determined from one document alone, refuse rather than combine
      information or guess.
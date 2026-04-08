skills:
  - name: retrieve_documents
    description: Load the three policy files and build a searchable index by document name and section number.
    input: "Document file paths (list of strings): policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt."
    output: "Structured index keyed by document_name -> section_number -> section_text."
    error_handling: "If any file is missing or unreadable, return a blocking error with the missing file names and do not produce policy answers."

  - name: answer_question
    description: Answer a policy question using a single source document with citation, or return the refusal template exactly.
    input: "User question (string) + indexed policy corpus from retrieve_documents."
    output: "Either: single-source answer with citation (document name + section number for every factual claim), OR exact refusal template text when not covered or ambiguous."
    error_handling: "If multiple documents are required to form one claim, or evidence is ambiguous/insufficient, refuse using the exact template instead of guessing."

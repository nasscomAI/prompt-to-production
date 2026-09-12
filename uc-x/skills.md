# skills.md

skills:
  retrieve_documents:
    purpose: >
      Load and index the three approved policy documents by document name
      and numbered section so questions can be answered from the correct
      source only.
    inputs:
      - policy_hr_leave.txt
      - policy_it_acceptable_use.txt
      - policy_finance_reimbursement.txt
    output: >
      A searchable collection of policy sections grouped by document.

  answer_question:
    purpose: >
      Search the indexed policy sections and return an answer from one
      source document only.
    rules:
      - "Return the relevant policy section when the question is covered."
      - "Include the document name and section number with every factual answer."
      - "Preserve all conditions and limits stated in the source section."
      - "Never combine claims from different policy documents."
      - "Never use hedging language or outside information."
      - "Return the exact refusal template when the question is not covered."

refusal_template: >
  This question is not covered in the available policy documents
  (policy_hr_leave.txt, policy_it_acceptable_use.txt,
  policy_finance_reimbursement.txt).
  Please contact [relevant team] for guidance.

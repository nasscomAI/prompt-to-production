skills:
  - name: retrieve_documents
    description: "Load all three policy files and index their content by document name and section number."
    input: "Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    output: "An index mapping each document and section number to its source text."
    error_handling: "Report missing, unreadable, empty, or unparseable documents and do not create substitute policy text."

  - name: answer_question
    description: "Find a single-source answer with a document and section citation or return the exact refusal template."
    input: "A natural-language question and the indexed policy documents."
    output: "One direct answer with source document and section citations, or the exact refusal template."
    error_handling: "Refuse questions not covered by the documents, cross-document ambiguity, and unsupported conclusions without hedging or invented guidance."

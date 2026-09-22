skills:
  - name: retrieve_documents
    description: Loads the three available policy documents and indexes their content by document name and section number.
    input:
      type: file_paths
      format: "List of paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt"
    output:
      type: indexed_documents
      format: "Collection of policy sections indexed by document name and section number"
    error_handling: >
      If any required policy document is missing, unreadable, or cannot be indexed, report the specific document error and do not answer policy questions using incomplete documents.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation or the exact refusal template.
    input:
      type: question
      format: "A staff policy question as plain text"
    output:
      type: answer
      format: "A policy answer citing document name and section number, or the exact refusal template when the question is not covered"
    error_handling: >
      Do not combine claims from different documents. Do not drop conditions from policy statements. Do not use hedging phrases. If the question is not covered by the documents, return the exact refusal template:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
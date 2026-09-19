skills:
  - name: retrieve_documents
    description: Loads all three policy files and builds an indexed catalog of structured sections and clauses by document name and section number.
    input: >
      A list of file paths (strings) pointing to the three policy files:
      policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A structured dictionary keyed by document filename containing metadata
      (title, reference, version) and an ordered list of sections and clauses
      with their section numbers, titles, and full verbatim text.
    error_handling: >
      If any of the three required policy files is missing, empty, or unreadable,
      raise a FileNotFoundError or ValueError and halt startup. Do not operate on
      partial document sets.

  - name: answer_question
    description: Searches the indexed policy documents for the single governing clause, returning a single-source answer with document name and section citation, or the exact refusal template.
    input: >
      A question string from the user, and the indexed catalog of policy documents
      from retrieve_documents.
    output: >
      A string response containing:
      (1) The direct answer preserving all conditions, numbers, and approvers;
      (2) Exact citation of the single source document filename and section number;
      OR the exact standard refusal template if the question is not covered.
    error_handling: >
      If the question cannot be answered from any document, or asks about external
      culture or unwritten norms, return the mandatory refusal template exactly:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact the relevant team for guidance."
      If an inquiry could potentially match multiple documents, enforce the
      single-source constraint: select the single authoritative policy or refuse cleanly.
      Never blend information from multiple documents or output hedging phrases.

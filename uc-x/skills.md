skills:
  - name: retrieve_documents
    description: Loads all policy text files and indexes them by document name, section number, and title.
    input: List or paths of policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Dictionary index of documents with section/clause mapping.
    error_handling: Handles missing policy files gracefully, raising FileNotFoundError if any input file is missing.

  - name: answer_question
    description: Searches document index for matching policy rules and produces single-source cited answer or exact refusal template.
    input: Question string and indexed policy documents object.
    output: Formatted answer string containing answer text and citation, or verbatim refusal template.
    error_handling: Returns exact refusal template when query matches no policy clause or creates cross-document ambiguity.

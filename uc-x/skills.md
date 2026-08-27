# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for quick retrieval.
    input: None. Accesses predefined context paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index or map of document segments, keyed by document name and section number.
    error_handling: Refuse to proceed if any of the three mandatory policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to find a specific answer and returns it with a citation, or returns the verbatim refusal template.
    input: A string representing the user's question.
    output: A string containing the single-source answer with document and section citation, or the exact refusal template.
    error_handling: Returns the refusal template if the answer requires blending information from multiple documents or if no relevant information is found.

skills:
  - name: retrieve_documents
    description: "Loads the three specific policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes them by document name and section number."
    input: "None; called automatically during application initialization."
    output: "A structured data object (dictionary or list) containing indexed policy sections for lookup."
    error_handling: "Terminates execution with an error message if any of the three mandatory policy files are missing or unreadable."

  - name: answer_question
    description: "Searches the indexed policy documents to provide a single-source response with a citation or the exact refusal template if the information is unavailable."
    input: "User query (string)."
    output: "A single-source response string (Direct Answer + Citation [Document Name Section Number]) or the exact refusal template string."
    error_handling: "Returns the exact refusal template for any question not found in the documents or if answering would require cross-document blending."

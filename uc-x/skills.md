skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them strictly by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index mapping document names to their respective numbered sections and content.
    error_handling: Notifies the user if any of the three documents fail to load or parse structurally.

  - name: answer_question
    description: Searches the indexed documents to return a single-source factual answer accompanied by a strict citation, or defaults to the hard refusal template if missing.
    input: The user's question as a string along with the indexed documents.
    output: The exact answer including document name + section citation, OR the exact verbatim refusal template.
    error_handling: Defers strictly to the refusal template if the search results cross-blend documents or if relevant explicit facts cannot be found.

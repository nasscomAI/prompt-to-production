skills:
  - name: retrieve_documents
    description: "Loads all 3 policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes them by document name and section number."
    input: "N/A"
    output: "JSON-formatted index of policy sections."
    error_handling: "Return file not found error if policy text files are missing from data directory."

  - name: answer_question
    description: "Searches the document index for relevant sections to return a single-source answer with citation or the exact refusal template."
    input: "User question (string)"
    output: "Answer with Source+Section citation OR verbatim refusal template."
    error_handling: "Strictly return verbatim refusal template if question is missing, ambiguous, or requires cross-document blending."

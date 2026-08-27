skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed text content structured by document name and section number.
    error_handling: Return an error to the user if any of the three policy documents cannot be loaded.

  - name: answer_question
    description: Searches indexed documents returning a single-source answer with a citation, OR the verbatim refusal template.
    input: An employee query string and the indexed policy documents.
    output: A single string containing either the answer with citation (document name + section number) OR the refusal template.
    error_handling: If rules from different documents conflict/blend, or if the answer is not in the documents, return the exact refusal template immediately.

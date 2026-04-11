skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes content by document name and section number.
    input: None (uses predefined paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt).
    output: A structured collection of policy clauses indexed by document and section.
    error_handling: Raises an exception if any policy file is missing or contains unparseable formatting.

  - name: answer_question
    description: Searches the indexed policy documents to provide a single-source answer with citations or returns the mandatory refusal template.
    input: A user query (string) and the indexed document collection.
    output: A string containing the answer with document and section citations, or the exact refusal template if no clear single-source answer is found.
    error_handling: Outputs the standard refusal template if the query is not covered, creates cross-document ambiguity, or would require prohibited blending.

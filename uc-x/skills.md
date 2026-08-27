skills:
  - name: retrieve_documents
    description: Loads the three policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt) and indexes their sections by document name and section number.
    input: An optional string representing the directory path containing the policy documents.
    output: A data structure (e.g., dictionary or list of dictionaries) containing the parsed section text, indexed by document name and section number.
    error_handling: Raise a FileNotFoundError if any of the three required policy files are missing from the directory.

  - name: answer_question
    description: Searches the indexed policy documents for the given question and returns either a single-source answer with document name and section number citation, or the exact refusal template if not found or if the query requires combining claims.
    input: A dictionary containing the user's question string and the indexed policy documents data structure.
    output: A string containing either the factual answer with source document and section citation, or the exact refusal template.
    error_handling: Return the exact refusal template if the question is invalid, out of scope, not covered in the documents, or if any ambiguity arises.

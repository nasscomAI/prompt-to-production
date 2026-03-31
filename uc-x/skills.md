skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`.
    output: Indexed text content categorised by document name and section number.
    error_handling: Raises an error if the files cannot be found or read.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the refusal template if the answer is not found or ambiguous.
    input: A user question and the indexed policy documents.
    output: A string containing the answer with citation (document name + section number) or the exact refusal template.
    error_handling: Returns the exact refusal template verbatim if the answer is not in the documents or if the question requires blending information from multiple documents.

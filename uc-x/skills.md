skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: File paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    output: Indexed dictionary of document sections and their content.
    error_handling: Return a FileNotFoundError if any file is missing, and an EmptyFileError if any file has no content.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with a citation, OR the refusal template.
    input: User question (string) and the indexed document dictionary.
    output: A single-source answer with citation (e.g., "Policy Name Section X.Y: Answer text") OR the exact refusal template if no match is found.
    error_handling: If the answer requires blending information from multiple documents or the model is unsure, it must default to the refusal template.

skills:
  - name: retrieve_documents
    description: Loads the available policy documents and extracts sections for indexing.
    input: File paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A dictionary indexed by document name and section number containing section text.
    error_handling: If a document cannot be read or contains no sections, an error is raised and execution stops.

  - name: answer_question
    description: Searches indexed policy documents and returns an answer based on a single document section with citation.
    input: Indexed policy documents and a user question string.
    output: A text answer referencing the document name and section number, or the refusal template if no relevant section exists.
    error_handling: If no relevant information exists in the documents, the system returns the refusal template exactly as defined.
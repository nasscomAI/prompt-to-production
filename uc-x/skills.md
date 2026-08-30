skills:
  - name: retrieve_documents
    description: Loads policy documents from disk and indexes their content by document name and section number.
    input: file_paths (list of string paths to policy document text files: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: indexed_documents (structured dictionary mapping document names and section numbers to text content and metadata).
    error_handling: Raises FileNotFoundError or IOError if any required policy document is missing or unreadable; logs the error and aborts indexing.

  - name: answer_question
    description: Searches indexed policy documents to retrieve a verified single-source answer with document name and section citations, or produces the refusal template if unaddressed.
    input: query (string question from user) and indexed_documents (structured dictionary produced by retrieve_documents).
    output: answer (string containing single-source factual response with document name and section citation, or the exact refusal template).
    error_handling: If the query cannot be answered from a single policy section, contains conflicting cross-document references, or is absent from all documents, outputs the exact refusal template verbatim without hedging or guessing.

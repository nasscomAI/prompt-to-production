skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of paths to policy text files (HR leave, IT acceptable use, Finance reimbursement).
    output: Structured representation mapping document name and section number to text content.
    error_handling: Log error and abort operation if any file is missing or unreadable.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User question as string and the structured documents index.
    output: Responds with answer string including source document name and section number, or refusal template.
    error_handling: Provide the exact refusal template if the answer is not found, or if answering requires blending information across multiple documents.

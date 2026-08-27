skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR leave, IT acceptable use, Finance reimbursement) and indexes them exactly by document name and section number.
    input: List of file paths to the 3 policy documents.
    output: Indexed text object mapped by document name and specific section number.
    error_handling: Raises an error and stops execution if any of the three required policy documents are missing, empty, or unreadable.

  - name: answer_question
    description: Searches the indexed documents to provide a single-source answer with exact citation, strictly refusing if the answer requires blending or isn't present.
    input: The user's question (string) and the indexed policy documents.
    output: An exact answer with source citation (document name + section number) OR the verbatim refusal template.
    error_handling: Returns the exact refusal template ("This question is not covered in the available policy documents...") if the answer cannot be found in a single section or requires blending multiple documents.

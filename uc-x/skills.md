skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to policy documents (e.g., ../data/policy-documents/*.txt).
    output: Indexed document content mapping document names and section numbers to text.
    error_handling: Fails cleanly if a document is missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the exact refusal template.
    input: A user question and the indexed policy documents.
    output: A single-source factual answer string with document and section citation, or the exact standardized refusal template.
    error_handling: Return the exact refusal template if the answer is not found, requires blending documents, or is otherwise ambiguous.

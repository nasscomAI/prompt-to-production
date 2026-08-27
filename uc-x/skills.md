skills:
  - name: "retrieve_documents"
    description: "Loads all 3 policy files and indexes them by document name and section number."
    input: "File paths to the 3 policy .txt files."
    output: "Indexed data structure containing document text and metadata."
    error_handling: "If a file is missing, the system must report a 'Document Retrieval Error' and stop."

  - name: "answer_question"
    description: "Searches indexed documents to return a single-source answer with citation or the refusal template."
    input: "User question (string) and indexed document data."
    output: "A single-source answer string with citation OR the exact refusal template."
    error_handling: "If multiple documents contain conflicting info, prioritize the primary document or refuse to avoid blending."
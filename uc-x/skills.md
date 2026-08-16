# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the 3 policy documents.
    output: A combined, indexed text representation of all documents.
    error_handling: If any file is missing, return an error and halt.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with a citation or the refusal template.
    input: User question and the retrieved documents.
    output: A precise answer citing document and section, or the exact refusal template.
    error_handling: If the answer requires blending two documents, or if it is not found, output the refusal template exactly.

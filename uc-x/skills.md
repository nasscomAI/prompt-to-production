# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the 3 policy documents.
    output: A single string containing the combined text of all documents, clearly labeled.
    error_handling: Raise an error if a document cannot be read.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: The user's question and the retrieved documents text.
    output: A string containing the answer and citation, or the refusal template.
    error_handling: If the question requires blending documents or the answer is not found, output the exact refusal template.

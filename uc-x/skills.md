```md
skills:

- name: retrieve_documents
  description: Loads all three policy documents and indexes them by document name and section number.
  input: Policy document files.
  output: Indexed policy documents for retrieval.
  error_handling: If a document or section is missing, return an appropriate error instead of guessing.

- name: answer_question
  description: Searches the indexed policy documents and answers using a single source with citation or returns the refusal template.
  input: A user question and indexed policy documents.
  output: A single-source answer with document name and section citation, or the required refusal template.
  error_handling: If the answer is not found or requires combining multiple documents, return the refusal template exactly.
```


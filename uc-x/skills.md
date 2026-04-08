- name: retrieve_documents
  description: Loads and indexes all policy documents by section.
  input:
    type: text files
    format: multiple policy documents
  output:
    type: dictionary
    format: {document_name: [{section, text}]}
  error_handling: >
    If any file missing, raise error.

- name: answer_question
  description: Answers user question using a single document source.
  input:
    type: question + indexed documents
  output:
    type: string
    format: answer with citation OR refusal template
  error_handling: >
    If answer requires combining documents, refuse.
    If no clear answer found, return refusal template.
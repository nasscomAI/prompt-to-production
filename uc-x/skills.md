# skills.md

skills:

- name: retrieve_document_clause
  description: Finds the relevant clause from a specific policy document based on the user’s question.
  input: User question (string) and policy document text (plain text).
  output: The most relevant clause or section from the document that answers the question.
  error_handling: If no relevant clause is found in the document, return a message indicating that the information is not available.

- name: answer_question_from_document
  description: Generates a clear answer to the user’s question using the retrieved clause from a single policy document.
  input: User question (string) and the retrieved clause text.
  output: A short answer that references the clause from the policy document.
  error_handling: If the clause does not clearly answer the question, return a refusal stating the answer cannot be determined from the provided document.
- name: retrieve_documents
  description: Loads all policy documents
  input: file paths
  output: combined text
  error_handling: return error if any file is missing

- name: answer_question
  description: Answers question from documents
  input: question and documents
  output: answer or refusal
  error_handling: return refusal if answer not found 
  
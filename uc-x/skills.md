

skills:
  - name: retrieve_documents
  description: Load and index policy documents by document name and section number.
  input:
    type: list
    format: List of file paths to policy documents
  output:
    type: dict
    format: Dictionary mapping document names to their section-wise content
  error_handling:
    - If a file is missing, return an error indicating which file could not be loaded
    - If file format is invalid, skip file and log error
    - If sections cannot be identified, treat entire document as a single section

- name: answer_question
  description: Answer user questions using a single policy document with citation or return refusal.
  input:
    type: string
    format: Natural language question from user
  output:
    type: string
    format: Answer with document name and section number OR refusal template
  error_handling:
    - If no relevant section is found in any document, return the refusal template exactly
    - If multiple documents contain partial answers, do not combine — return refusal
    - If ambiguity exists across documents, return refusal
    - If answer lacks a clear section reference, do not return it — instead refuse

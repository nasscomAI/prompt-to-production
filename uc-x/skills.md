skills:

## 1) name: retrieve_documents
  - description: Loads policy documents and indexes them by document name and section number.
  - input: List of file paths to policy documents (.txt)
  - output: Dictionary structured as {document_name: {section_number: text}}
  - error_handling: Returns empty structure if file read fails; skips malformed sections

## 2) name: answer_question
  - description: Retrieves a single-source answer with citation or returns a refusal message if not found.
  - input: Question string and indexed document dictionary
  - output: Answer string with document citation or refusal template
  - error_handling: Returns refusal template if question cannot be answered from a single document or is ambiguous

# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: file paths to the 3 policy documents
    output: structured documents with section numbers
    error_handling: Return error if files missing

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: user question and structured documents
    output: string response with citation OR exact refusal template
    error_handling: Refuse exactly with the template if the answer is cross-document or not explicitly found

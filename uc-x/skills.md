skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section
    input: file paths
    output: indexed docs
    error_handling: handles read errors
  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: question string
    output: answer string
    error_handling: uses refusal template

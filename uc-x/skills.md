skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: None
    output: A comprehensive index mapping document names and their section headers to raw texts.
    error_handling: System exits if any of the three required policy documents is missing.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: string (user query)
    output: string (exact policy text or refusal block)
    error_handling: Must return the exact refusal template string if the query cannot be definitively mapped to a single source.

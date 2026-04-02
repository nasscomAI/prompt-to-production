skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: list of policy file paths
    output: dictionary containing indexed document content by document name and section number
    error_handling: returns "Failed to load" if any document cannot be parsed.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: user query string
    output: strict, single-source answer with document name and section number citation, or refusal template
    error_handling: if information is missing or ambiguous across documents, return exact refusal template: "This question is not covered in the available policy documents..."

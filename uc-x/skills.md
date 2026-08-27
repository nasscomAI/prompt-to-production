skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: file paths to policy documents
    output: indexed dictionary of document sections
    error_handling: Raises error if any file fails to load.
    
  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: Question string and indexed documents.
    output: String response containing the exact citation or refusal template without cross-document blending.
    error_handling: If genuinely ambiguous, not perfectly captured by single-source sections, or relying on multiple documents, explicitly output exactly the refusal template.

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: List of paths (strings) to the policy text files
    output: Indexed text mappings grouped by document name
    error_handling: Return error if any required files are missing or unreadable

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: User question string and the retrieved document index
    output: Formatted string containing either a verified single-source answer with section citation or the exact refusal template
    error_handling: Return the verbatim refusal template immediately if data is missing or ambiguous across documents

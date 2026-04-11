skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and indexes them strictly by document name and section number.
    input: File paths to the three required policy .txt documents.
    output: A structured index mapping document names and section numbered headers to their verbatim text.
    error_handling: System halt if any required document is missing or unreadable.

  - name: answer_question
    description: Queries indexed documents to return a single-source answer with a mandatory citation, or explicitly refuses using the verbatim template.
    input: The user's query string and the indexed document structure.
    output: A compliant answer string with `[Document Name, Section X.Y]` appended, OR the exact verbatim refusal template.
    error_handling: Any ambiguity crossing more than one document immediately defaults to the strict refusal template.

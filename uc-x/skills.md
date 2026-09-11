@'
skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number for lookup.
    input: "Paths to the three policy .txt files."
    output: "An index mapping (document_name, section_number) to section text, covering all three documents separately."
    error_handling: >
      If any of the three files is missing or unreadable, raise a clear
      error naming which file failed, rather than proceeding with partial
      documents. Documents are never merged into a single combined index -
      each stays tagged with its own source document name.

  - name: answer_question
    description: Searches the indexed documents for a single document/section that answers the question, and returns a cited answer or the refusal template.
    input: "A user question (string) and the document index from retrieve_documents."
    output: "Either an answer string with a document+section citation, or the exact refusal template string."
    error_handling: >
      If the question could only be answered by combining two different
      documents, this counts as an invalid match - return the refusal
      template rather than blending. If a match is found but is genuinely
      ambiguous between two documents, also return the refusal template.
      Never guess or hedge with soft language.
'@ | Set-Content -Path skills.md -Encoding utf8
# skills.md
skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: A dict of {document_name: file_path} for the 3 policy files.
    output: A dict of {document_name: [ {doc, clause, text}, ... ]} — every numbered clause parsed out individually.
    error_handling: If any required document file is missing, raises a clear error rather than proceeding with partial document coverage.

  - name: answer_question
    description: Searches indexed documents for a question and returns either a single-source cited answer or the exact refusal template.
    input: question (str), the document index from retrieve_documents.
    output: A string — either "<clause text>\n[Source: <doc>, Section <id>]" or the exact refusal template.
    error_handling: If the question matches content in more than one document with comparable confidence, refuses rather than blending the two into one answer.

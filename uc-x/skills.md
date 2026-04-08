skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None required.
    output: Indexed corpus of policy documents structured by document name and section number.
    error_handling: Return an error if any policy file is missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation or the exact refusal template.
    input: A user query string.
    output: A single-source factual answer including source document name and section number, or the exact refusal template.
    error_handling: Output the exact refusal template if the answer is completely missing, or if answering requires blending claims from two different documents.

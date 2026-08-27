skills:
  - name: retrieve_documents
    description: Opens all three specific policy files and indexes them strictly by document name and section number to prevent blending.
    input: None required explicitly (hardcoded to scan ../data/policy-documents/).
    output: A cleanly isolated dictionary mapping each document to its structured numbered sections.
    error_handling: Raise an exception immediately if any referenced file fails to load.

  - name: answer_question
    description: Searches indexed documents sequentially for an exact match to the query, returning a single-source answer with verbatim citations.
    input: The user's literal query string and the indexed documents object.
    output: A heavily structured answer containing the document name and section number, OR the exact verbatim refusal template.
    error_handling: Never hedge on ambiguity. If an answer requires bridging two documents, instantly revert to the standard refusal template.

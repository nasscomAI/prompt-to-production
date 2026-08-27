skills:
  - name: retrieve_documents
    description: "Loads all three policy files (HR, IT, Finance) and indexes them by document name and section number for easy retrieval."
    input: "N/A - Reads predefined policy files in ../data/policy-documents/."
    output: "A dictionary or index containing section-by-section text from all three documents."
    error_handling: "If any of the three files are missing or unreadable, stop processing and alert the user."

  - name: answer_question
    description: "Searches the indexed policy documents and returns a cited, single-source answer or the verbatim refusal template."
    input: "User query (String)."
    output: "Answer string with citation OR refusal template."
    error_handling: "If the question creates ambiguity across multiple sources, use the refusal template to avoid blending. Refuse if asked about general workplace culture or flexible working not in the source text."

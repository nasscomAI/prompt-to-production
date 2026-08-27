# skills.md
# UC-X document QA skills definitions.

skills:
  - name: retrieve_documents
    description: Load all policy text documents and index them by document name and section number.
    input: List of document file paths.
    output: Dict mapping document names to section dictionaries (section_id -> section_text).
    error_handling: If a file cannot be read, raise an error and abort. If no numbered sections are found, return an empty dict for that document.

  - name: answer_question
    description: Search indexed documents for a single-source answer and return a citation, or refuse using the exact refusal template.
    input: Indexed document dictionary and a question string.
    output: Either a factual answer with "Source: <document> section <id>" or the refusal template.
    error_handling: If the question is not covered by any document, return the refusal template exactly; if the answer requires blending from multiple documents, return the refusal template exactly.

# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy text documents and parses/indexes them by filename and section/clause number.
    input: None. Loads standard paths for policy documents.
    output: dict mapping filenames (str) to list of sections, each having section number (str) and content (str).
    error_handling: Logs warning and continues if one or more policy files are missing.

  - name: answer_question
    description: Searches the indexed sections to retrieve a single-source answer with proper citation, or outputs the refusal template.
    input: query (str) representing the user's question.
    output: answer_text (str) with factual content and citation, or the refusal template.
    error_handling: Returns the exact refusal template if no relevant information is found or if the query lies outside the policies' scopes.

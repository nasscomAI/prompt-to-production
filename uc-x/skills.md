# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them cleanly by document name and section number.
    input: File paths to the three required policy .txt documents.
    output: A searchable index mapping document names and section numbers to their text content.
    error_handling: Fail critically and refuse operation if any of the three documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the strict refusal template.
    input: User's question string and the retrieved document index.
    output: A definitive answer string citing exactly one document and section, or the exact refusal template verbatim.
    error_handling: If an answer requires blended information from multiple documents (creating ambiguity), immediately return the refusal template instead of combining them.

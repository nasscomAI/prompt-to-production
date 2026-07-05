skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes each by document filename and section number.
    input: The fixed UC-X policy file paths under ../data/policy-documents/.
    output: A nested mapping of document filename to section number to section text.
    error_handling: Missing or unreadable files are represented by an empty document index so the CLI can refuse instead of crashing.

  - name: answer_question
    description: Answers a user question from one policy section with citation or returns the exact refusal template.
    input: A user question string and the indexed documents from retrieve_documents.
    output: A single-source answer containing document filename and section number, or the required refusal text.
    error_handling: Unknown questions, missing sections, missing documents, and questions that could require multiple documents all return the exact refusal template.

# skills.md

skills:
  - name: retrieve_documents
    description: Load all three corporate policy documents and index them by document name and section number.
    input: None or list of policy file paths.
    output: Indexed policy content structured by document name and section/clause number.
    error_handling: If any of the documents fail to load or are missing, log the error and notify the system.

  - name: answer_question
    description: Search the indexed policy documents for a given query and return a single-source answer with document name and section number citation, or return the verbatim refusal template if the answer is not present or is ambiguous.
    input: A question query (string) and the indexed policy content.
    output: A single-source answer (string) with citation, or the exact refusal template.
    error_handling: If the query is empty or the index is missing, return the refusal template.

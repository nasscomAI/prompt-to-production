# skills.md — UC-X Policy Q&A Agent (Ask My Documents)

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents from the policy directory, structuring text by document filename and section/clause numbers.
    input: docs_dir (str: path to policy documents directory).
    output: dict containing indexed documents, section headers, clause identifiers, and search mappings.
    error_handling: Raises FileNotFoundError if the policy directory or essential policy files are missing, and logs any parsing anomalies.

  - name: answer_question
    description: Matches a user query against indexed policy clauses, generates a verified single-source answer with exact document and section citations, or returns the standardized refusal template if uncovered.
    input: query (str: user question), index (dict: indexed policy documents).
    output: str (verified single-source answer with document name and section citation, or exact refusal template).
    error_handling: Strictly refuses cross-document synthesis and ungrounded queries by returning the exact refusal template.

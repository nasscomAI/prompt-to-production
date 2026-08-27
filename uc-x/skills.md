# skills.md — UC-X Policy Q&A

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files, indexes them by document name and section number, and returns a structured context string ready for inclusion in a prompt.
    input: A list of file paths (strings) pointing to the three policy .txt files.
    output: A dict with keys 'context' (a single formatted string containing all three documents with clear document-name headers) and 'doc_names' (list of the three filenames, used in the refusal template).
    error_handling: If any file is missing or unreadable, raise FileNotFoundError naming the specific file — never silently skip a document, as a missing doc could cause the system to answer "not covered" for questions it should answer.

  - name: answer_question
    description: Sends a user question together with the full indexed policy context to Claude, returning a single-source answer with section citation or the exact refusal template if the question is not covered.
    input: question (string), policy_context (string from retrieve_documents), conversation_history (list of prior turn dicts for multi-turn context).
    output: A string — either a cited answer ending in [document_name · section X.Y] or the exact refusal template with no additional text.
    error_handling: If the Claude API call fails, print an error message and return a fallback string indicating a technical error rather than an empty response or a hallucinated answer. Never return a partial or uncited answer.

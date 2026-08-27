# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes their contents by document name and section number.
    input: None (uses hardcoded paths to the policy documents)
    output: Indexed data structure containing the text of each document mapped to its specific sections.
    error_handling: Raise an explicit error if any of the three policy files are missing or cannot be read.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation, or the refusal template.
    input: The user's question (string) and the indexed policy documents.
    output: A factual answer citing the source document name and section number, OR the exact refusal template.
    error_handling: If the question is not covered, or if answering would require blending claims from two different documents, return the exact refusal template. Do not raise an exception or guess.

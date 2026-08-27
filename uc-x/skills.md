# skills.md — UC-X Document Retrieval & Q&A Skills

skills:
  - name: retrieve_documents
    description: Loads all policy files and indexes them by document name and section number for precise retrieval.
    input: List of paths to the 3 policy .txt files.
    output: A structured index where each document name is mapped to its numbered sections and content.
    error_handling: Return a fatal error if any policy file is missing or contains unparseable section numbering.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer and applies strict enforcement rules before responding.
    input: A user question and the indexed policy data.
    output: A cited answer (Document name + Section #) OR the mandatory refusal template.
    error_handling:
      - If the answer logic requires blending information across two documents, the skill must return the refusal template.
      - If no exact section match is found for the query, the skill returns the refusal template.
      - If an answer is found but lacks a clear section number for citation, the skill must refuse to answer.
      - Detect and reject any "hedging" language in the generated response before outputting.
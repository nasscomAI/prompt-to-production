# UC-X Policy Retrieval Skills

skills:
  - name: retrieve_documents
    description: Loads all policy text files and parses them into a structured index organized by document name and section number to prevent data omission.
    input: Directory path containing the policy .txt files.
    output: A nested dictionary mapping document names to section numbers and their associated text.
    error_handling: Logs an error if a mandatory file is missing but continues to index available documents.

  - name: answer_question
    description: Perfroms a keyword-aware search across indexed documents to find the single most relevant section that answers the query without hedging or blending.
    input: User query string and the indexed document structure.
    output: A cited answer string (Source + Section) or the exact refusal template if the answer is missing.
    error_handling: If no single-source match exceeds the relevance threshold, the skill must return the exact refusal template to prevent hallucination.


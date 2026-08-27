# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes them by document name and section number
    input: list of file paths
    output: structured documents with sections
    error_handling: If any document is missing or unreadable, return an error and stop execution. Ensure all documents are loaded before answering.

  - name: answer_question
    description: Answers user questions strictly using a single document source with citation
    input: user question
    output: answer with document name and section number OR refusal template
    error_handling: 
      - If no relevant section is found, return the refusal template exactly
      - If multiple documents contain relevant information, do not combine — choose one or refuse
      - Do not use hedging phrases or assumptions
      - If ambiguity exists, return refusal instead of guessing

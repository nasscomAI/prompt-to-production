# skills.md

skills:
  - name: retrieve_documents
    description: Loads the designated HR, IT, and Finance policy files into memory and logically indexes them by document name and section number for precise retrieval.
    input: File paths to the three policy `.txt` files.
    output: An indexed dictionary mapping each document and section number to its verbatim text content.
    error_handling: Refuse to initialize if any policy file is missing or corrupted, ensuring the agent never operates with an incomplete context window.

  - name: answer_question
    description: Searches the indexed sections to identify the single most relevant source for a user's question, extracts the exact rule, and prepends the required citation.
    input: The user's question string and the indexed documents dictionary from retrieve_documents.
    output: A single string containing the cited answer, or the exact verbatim refusal template if the answer is absent or requires dangerous cross-document blending.
    error_handling: If a question spans multiple documents (e.g., HR remote work tools + IT personal devices), refuse the synthesis and strictly return the restrictive single-source constraint or the refusal template to avoid hallucinated permissions.

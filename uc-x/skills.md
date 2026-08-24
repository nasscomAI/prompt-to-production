# skills.md

skills:
  - name: retrieve_documents
    description: Safely loads all 3 policy txt files into memory, retaining the context of their file names to be used for explicit citations.
    input: List of paths to the policy `.txt` files.
    output: A compiled context string mapping each document's name to its full text content.
    error_handling: Fail safely if a document is missing by alerting the user.

  - name: answer_question
    description: Takes the user's query and the documents as a context bundle. Searches the indexed documents to return either a single-source cited answer or strictly the refusal template.
    input: The user's question string and the compiled document context.
    output: A compliant text response preserving the refusal template or citation requirements.
    error_handling: Return the literal refusal template if the LLM encounters a parsing error or ambiguity.

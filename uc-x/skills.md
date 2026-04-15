# skills.md — UC-X

skills:
  - name: retrieve_documents
    description: Loads all 3 policy txt files from the data directory and indexes them natively by their filename to ensure strict compartmentalization.
    input: File paths to the 3 policy documents.
    output: A structured string map containing the full text of each document properly segmented and labeled by its exact filename.
    error_handling: Handles missing files gracefully by notifying the user.

  - name: answer_question
    description: Executes the Gemini LLM with the consolidated index and strict RICE rules, ensuring zero multi-document blending.
    input: Indexed documents context string and the User's question.
    output: A strictly compliant answer citing a single source OR the exact verbatim refusal template.
    error_handling: In case of LLM failure or API timeout, securely falls back to the rigid refusal template.

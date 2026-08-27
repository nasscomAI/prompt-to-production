# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    This template goes verbatim into your RICE Enforcement and agents.md.
    It is what prevents hedged hallucination — the system has a required response format that leaves no room for "while not explicitly covered..."
    input: File paths to the 3 policy .txt files.
    output: A structured index of all sections from the documents, tagged by document name and section number.
    error_handling: If any file is missing, return an error stating which document could not be loaded.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: The user's question and the structured index of documents.
    output: A text answer containing citations (document name + section number) or the exact refusal template.
    error_handling: If the question requires blending information from multiple documents, refuse to answer or answer from only one document if appropriate. If the answer is not explicitly found, return the exact refusal template without any preamble or hedging.

# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads the three policy text files, parses sections, and builds an in‑memory index for fast lookup.
    input: None (no external input).
    output: Dictionary mapping document names to a list of sections, each with 'section' (e.g., "2.3") and 'content' (full text of that section).
    error_handling: Raises an exception if any file is missing; logs error and aborts execution.


  - name: answer_question
    description: Given a user query, searches the indexed documents for matches. If a single document provides a clear answer, returns the exact sentence(s) with citation (document name and section). If no single document matches or multiple documents are needed, returns the refusal template exactly.
    input: String query from the CLI.
    output: String answer with optional citation or the refusal template.
    error_handling: Returns the refusal template for ambiguous or unsupported queries.


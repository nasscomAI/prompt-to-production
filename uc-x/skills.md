skills:
  - name: retrieve_documents
    description: Loads all policy text files and indexes them by document name and section number.
    input: 
      - file_paths (list of strings): Paths to the policy .txt files.
    output: 
      - indexed_content (dict): Document names mapping to their section-by-section contents.
    error_handling: "Fail cleanly if any file is unreadable."

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citations or the exact refusal template.
    input:
      - question (string): The user's query.
      - indexed_content (dict): The loaded policy documents.
    output: 
      - answer (string): The final response adhering strictly to the enforcement rules.
    error_handling: "If multiple documents seem to match but don't align perfectly, fall back to the exact refusal template."

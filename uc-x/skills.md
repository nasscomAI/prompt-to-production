# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: Paths to policy text files (list of strings).
    output: Indexed documents (dict) with document name, section number, and section content.
    error_handling: If any file is missing or unreadable, returns an error message and skips that document.

  - name: answer_question
    description: Searches indexed documents for the question, returns a single-source answer with citation or the refusal template if not found.
    input: Question (string), indexed documents (dict).
    output: Answer (string) with citation (document name and section number), or refusal template if not covered.
    error_handling: If question is ambiguous or not found, returns refusal template exactly as specified.

# skills.md — UC-X Policy Question Answering

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number for efficient searching.
    input: List of file paths to the three .txt policy documents (list of strings).
    output: Indexed data structure (e.g., dictionary) with document names as keys, containing sections with numbers and text.
    error_handling: Raises an error if any file is missing, unreadable, or does not contain numbered sections.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source answer with citation or the refusal template.
    input: Question (string) and indexed documents (data structure).
    output: Answer string with citation (e.g., "policy_hr_leave.txt section 2.6: ...") or exact refusal template.
    error_handling: Uses refusal template if question is not found in any single document; refuses to combine sources or hedge.

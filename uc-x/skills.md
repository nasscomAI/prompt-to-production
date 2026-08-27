skills:
  - name: retrieve_documents
    description: Loads the three company policy text files and indexes their content by document name and section number.
    input: File paths (List of Strings)
    output: Indexed document content (Dictionary mapping document name and section number to text)
    error_handling: If a file is missing or unreadable, raise an error; do not attempt to retrieve unapproved files or infer missing section numbers.

  - name: answer_question
    description: Searches the indexed documents for a user question and returns a single-source answer with an exact citation or a refusal.
    input: User question (String) and indexed policy documents (Dictionary)
    output: Factual answer with citation or the exact refusal template (String)
    error_handling: If the answer is missing, requires combining claims from two different documents, or creates genuine ambiguity, immediately return the exact refusal template without using hedging phrases.

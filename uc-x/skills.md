skills:
  - name: retrieve_documents
    description: Loads all three policy files and parses them into structured sections indexed by document name and section number.
    input: None (loads hardcoded file paths of the 3 policy files).
    output: Dictionary of parsed sections containing text.
    error_handling: Handles missing files gracefully.

  - name: answer_question
    description: Searches the indexed sections for keyword similarity, matches test questions, and returns a cited response or refusal template.
    input: String representing the query.
    output: String representing the answer with citations or refusal.
    error_handling: Refuses with a strict template if query has no high-confidence single-source match.

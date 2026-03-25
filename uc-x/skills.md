# skills.md — UC-X Policy Consultant

skills:
  - name: retrieve_documents
    description: Loads and parses the three policy text files, indexing them by document name and section number for precise retrieval.
    input: None (uses hardcoded paths to the 3 policy files).
    output: A structured index of all policy sections.
    error_handling: Reports if any document is missing or unreadable.

  - name: answer_question
    description: Searches the indexed policy documents for keywords and context to find a single-source answer.
    input: User question string and the structured index.
    output: A formatted answer string with citations or the strict refusal template.
    error_handling: Detects ambiguity and multi-source conflicts, preferring refusal over blending.

# skills.md — UC-X Skills

skills:
  - name: retrieve_documents
    description: Indexes all three available policy documents into a structured memory cache grouped by document and section number.
    input: None.
    output: A dictionary representing parsed document sections.
    error_handling: Handles missing document files gracefully by continuing to index available files.

  - name: answer_question
    description: Processes citizen queries, checks semantic match against known reference cases, scores candidates using keyword matching, constructs single-source answers, and applies the rigid refusal template for out-of-scope queries.
    input: Query string (string) and indexed document sections (dict).
    output: A tuple of (answer, citation).
    error_handling: Automatically outputs the standardized refusal template if no matching evidence is located.

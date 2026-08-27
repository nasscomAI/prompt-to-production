# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy files and parses them into a structured index by document name and section number.
    input: None (uses hardcoded paths to the 3 policy files).
    output: A dictionary indexing sections (e.g., index["policy_hr_leave.txt"]["2.3"] = "text").
    error_handling: Logs an error and fails to initialize if any of the 3 core files are missing.

  - name: answer_question
    description: Searches the indexed sections for keywords related to the user's question and returns a cited answer or the refusal template.
    input: User's question string and the indexed documents dictionary.
    output: A string containing the answer with [Source Section] or the exact refusal template.
    error_handling: Returns the refusal template if the search yields multiple conflicting sources without a clear primary policy or if no source is found.

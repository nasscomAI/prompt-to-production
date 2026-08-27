# skills.md

skills:
  - name: retrieve_documents
    description: Loads policy document files and parses them into a searchable index by document name and section number.
    input: List of document filenames or paths (e.g., ['policy_hr_leave.txt', ...]).
    output: Indexed text structure organized by document and section.
    error_handling: Return error if files are missing or formatting prevents parsing.

  - name: answer_question
    description: Searches the indexed documents to find a single-source answer for the user query, including the section citation.
    input: User prompt (String), Indexed policy data.
    output: Single-source answer with document and section citation, or the mandatory refusal template if no match is found.
    error_handling: Refuse to answer if information would require blending across multiple documents or if no document provides a clear answer.

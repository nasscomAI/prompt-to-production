# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy text files (HR, IT, Finance) into structured section blocks searchable by keywords and topics.
    input: List of file paths to policy documents or directory path.
    output: Dictionary mapping document names and section IDs to text content.
    error_handling: Raises FileNotFoundError if any policy file is missing; logs warnings for unparsed sections.

  - name: answer_question
    description: Evaluates a user query against indexed policy sections, enforcing single-source attribution, exact section citations, and refusal templates.
    input: String question and indexed policy dictionary from retrieve_documents.
    output: Formatted string answer containing exact section citation OR exact refusal template.
    error_handling: Returns exact refusal template if no matching section is found or if query requires unevidenced cross-document blending.

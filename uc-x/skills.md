# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy txt files and parses them into a searchable index mapped by document name and section number.
    input: List of file paths to the policy documents.
    output: A nested dictionary structure indexing text by document and section.
    error_handling: System exits if any of the three reference policies are missing.

  - name: answer_question
    description: Searches the indexed policies for the closest matching clause to answer a user's question safely, or returns the strict refusal template.
    input: The user's question string and the parsed document index.
    output: A fully compliant string containing a single-source answer with a section citation, OR the exact verbatim refusal template.
    error_handling: If the intent spans multiple conflicting documents, refuse execution using the strict template.

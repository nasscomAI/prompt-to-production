# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: List of file paths to policy documents.
    output: Indexed structured data mapping document names and section numbers to content.
    error_handling: Return an error if documents fail to load or lack identifiable sections.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: The user's question and the indexed structured document data.
    output: A factual string answer with explicit citing (document + section), or the exact refusal template.
    error_handling: If the question spans multiple documents creating ambiguity or is not explicitly covered, output the exact refusal template instead of guessing.

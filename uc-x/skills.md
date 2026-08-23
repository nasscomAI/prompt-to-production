# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: none
    output: A structured index of all policy documents, detailing the section number and exact string paragraph text for that section.
    error_handling: Handles missing files gracefully. If a document cannot be accessed, warns the user that policies may be incomplete.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: String - User question about company policies.
    output: String - Either the exact citation from a specific section of one document (including its name and section), or the verbatim refusal template.
    error_handling: Returns the exact refusal template if there is ambiguity, cross-document blending required, or if no section perfectly satisfies the question alone.

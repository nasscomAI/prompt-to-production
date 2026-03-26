# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all 3 approved policy files and parse them into indexable structures by document name and section number.
    input: List of file paths to policy documents (e.g., HR, IT, Finance).
    output: A dictionary or indexed structure containing document text mapped by filename and section.
    error_handling: "Fail execution if a permitted document is missing."

  - name: answer_question
    description: Search indexed documents to return a single-source precise answer with citation OR a clean refusal template.
    input: Employee question as a string.
    output: Formatted string containing either a cited policy answer or the exact refusal template.
    error_handling: "If multiple documents conflict or the question requires blending context (e.g., 'personal phone' spanning HR and IT), immediately return the exact refusal template."

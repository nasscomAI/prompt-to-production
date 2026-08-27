# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy documents, parses them into sections, and indexes content by document name and section number.
    input: "No arguments; uses the three policy files from ../data/policy-documents/"
    output: "A structured document index containing document names, section numbers, and the associated text for each section."
    error_handling: "If a policy file is missing or unreadable, raise an error and stop rather than guessing."

  - name: answer_question
    description: Searches the indexed policy content for a single-source answer and returns a grounded response with citation or the required refusal template.
    input: "A question string and the indexed policy documents"
    output: "A response string containing either the answer with source citation or the exact refusal template when the answer is not covered."
    error_handling: "If multiple documents appear relevant or the answer cannot be supported by one source, return the refusal template instead of blending information."
